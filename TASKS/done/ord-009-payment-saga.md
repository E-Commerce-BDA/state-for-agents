# ord-009 — order-svc: pending-first payment saga

## What

Checkout captured the card **before** the order row existed: the provider was
called with the literal `'order-temp'` as its reference, then the order was
inserted directly as `confirmed`/`paid`. A database failure after the capture
took the money and left nothing behind, there was no state that could describe
"we are in the middle of this", a post-capture failure had no refund, and the
six-digit `#2026-\d{6}` number could collide into a 500 after the charge.

The order is now the **first** durable write and it is written as `pending`:
`TX1` (order + items + history + pending payment + idempotency key) → capture
(provider key = order id) → `TX2` (payment → captured, order → confirmed/paid,
outbox `order.created`). A failure records the phase it reached and undoes
exactly that much, and a retry on the same key **resumes** the pending attempt
instead of refusing it.

## How

- `src/checkout/checkout.repository.ts` — `findPendingPayment`, `confirmOrder`
  (TX2, guarded on `status = 'pending'`, writes history `pending → confirmed`)
  and `failOrder` (closes a pending attempt, records the payment outcome, and
  returns `false` when the order was already settled so a replay is harmless).
- `src/checkout/checkout.service.ts` — `placeOrder` tracks a `SagaPhase`
  (`pricing → persisting → persisted → captured`); `capture`, `recover`,
  `resumeSaga`, `rollBackCapture`, `closeAttempt`, `releaseHold`,
  `refundQuietly`, `orderCreatedEvent`. `replayStoredAttempt`'s `pending` branch
  now resumes.
- `src/clients/clients.module.ts` — one owner for `CatalogClient`/`CartClient`,
  imported by `CheckoutModule` and `OrdersModule`.
- `src/orders/orders.service.ts` — `updateStatus` releases the hold after a
  terminal (`cancelled`/`failed`) transition commits; `OrdersModule` imports
  `ClientsModule`.
- Tests: `checkout.service.spec.ts` (19 → 25 cases, repository mocked),
  `orders.service.spec.ts` (hold release), and a `payment saga` block in
  `test/checkout.e2e-spec.ts` that runs a real app with a fake provider.

## Decisions (+ one rejected alternative each)

- **Pending first, capture second.** The order row is the record of intent, so
  it must exist before any money moves. Rejected: capture first and compensate
  on failure — the compensation is a refund, which is a second money movement
  that can itself fail; the "nothing left behind" case cannot be repaired.
- **The provider idempotency key is the order id, not the reservation id.** The
  order id is the durable identity a resume can re-derive from the row.
  Rejected: keep the reservation id, which a resumed attempt would have to
  retrieve from the order anyway.
- **A decline is terminal, a thrown error is not.** `success: false` closes the
  attempt (`failed`/`failed`, history `pending → failed`, hold released, 402
  `PAYMENT_FAILED`); a provider exception leaves the row `pending` **and keeps
  the hold** (503 `PAYMENT_UNAVAILABLE`) so the retry can resume. Reason: a
  decline cannot be retried, an exception might have been a timeout on a
  capture that actually succeeded. This consciously deviates from "every path
  releases the hold exactly once" — releasing it under a pending order would let
  the resume confirm stock that had already been given back. Rejected: release
  the hold on both, which trades an oversell for a bound hold.
- **`TX2` failure refunds, then closes.** A capture without a confirmation is
  money for an order nobody can see, so it is refunded, the order is closed as
  `failed`/`refunded`, the hold is released, and the customer gets 503
  `PAYMENT_PERSIST_FAILED` — not a generic 500. A failed refund is logged loudly
  and still returns the same code, because the alternative is pretending the
  payment did not happen. Rejected: leave the order pending and let the retry
  capture again (a second charge for the same order is exactly what the saga
  exists to prevent).
- **The retry resumes; it does not start over.** `findByIdempotencyKey` +
  `findPendingPayment` re-derive totals, transaction and hold from the rows, so
  there is one order, one reservation and one confirmation. Rejected: burn the
  key on any failure and make the customer re-enter the checkout.
- **Order-number collisions are retried inside the insert** (max 3 draws, keyed
  on `err.constraint`), so the six-digit number stays human-readable without a
  schema object or an enumerable sequence. Rejected: a DB sequence, and
  accepting a 500 after the capture.
- **The losing insert race no longer refunds anything.** With the capture after
  the insert, the loser has not captured yet — it only releases its own hold and
  replays the winner, which may itself be pending. Rejected: keep the losing
  path's refund, which was only correct while the capture came first.
- **The saga is exposed through the repository, not through the service.** Every
  phase can be failure-injected by replacing one collaborator, and the e2e
  provider fake reads the order row at capture time — the structural proof that
  no authorisation happens before the row exists. Rejected: stubbing `pg`.
- **`ClientsModule` instead of importing `CheckoutModule` into `OrdersModule`.**
  Orders needs catalog for the hold release; the reverse dependency would become
  a cycle once checkout needs the orders repository. Rejected: duplicate
  providers (two instances) or a module cycle.

## Verification

All commands from `order-svc` on 2026-10-30:

| Gate | Result |
|---|---|
| `pnpm lint` (oxlint --type-aware) | 69 files, 0 warnings, 0 errors |
| `pnpm test` | 6 files / 70 tests passed (`checkout.service` 25, `orders.service` 17) |
| `pnpm test:e2e` | 6 files / 71 passed, 1 skipped (live catalog) |
| `pnpm build` (`nest build`, includes `tsc --noEmit`) | clean |

Behaviour proven by `test/checkout.e2e-spec.ts` (real Postgres + Redis, fake
provider):

1. the provider reads the order row **at capture time** — it exists, and it is
   `pending`/`pending`; after `TX2` the payment holds the capture's
   `transaction_id` and history is `[null → pending, pending → confirmed]` with
   exactly one `order.created` outbox row;
2. a declined card → 402 `PAYMENT_FAILED`, order `failed`, payment `failed`,
   history `pending → failed`, **no** outbox row, hold released once, and the
   same key afterwards → 409 `ORDER_ATTEMPT_CLOSED` with no second capture;
3. `confirmOrder` forced to throw → 503 `PAYMENT_PERSIST_FAILED`, one refund for
   the capture's `transaction_id` and grand total, order `failed`/`refunded`,
   payment `refunded`, no outbox row, hold released once;
4. a transient capture error → 503 `PAYMENT_UNAVAILABLE`, row stays `pending`,
   hold **not** released; retrying the same key → 201 with the same
   `orderId`/`orderNumber`, one order, one reservation, two capture attempts
   both against a still-pending row, one `order.created` carrying the original
   `reservationId`.

Unit coverage adds the phase matrix (persisting → 503 `CHECKOUT_UNAVAILABLE`,
capture decline → 402, transient → hold kept, `TX2` → refund + close + release,
resume, missing pending payment → 409) and the orders hold release (once, after
the commit, best-effort).

Commits: `4dfdf31` clients module · `38d0523` saga · `8291eb8` orders hold
release · `9d52040` unit + e2e failures.

## Follow-ups

- The hold is skipped for a transient capture failure, so a resume that happens
  after the reservation TTL confirms an order whose stock was released. A
  compensating re-reserve on resume (or a hold TTL that outlives the retry
  window) is needed before the storefront retries automatically.
- `failOrder` closes only `pending` rows; once `ord-010` adds the refunds
  ledger, the refund path there must not double-close an attempt the saga
  already closed as `refunded`.
- A crash **between** capture and `TX2` is only repaired by the customer's
  retry (resume). A sweeper over `payments.status = 'pending'` older than N
  minutes should reclaim it server-side (`ord-011` candidate).
- `orders.status` history has no `pending → expired` transition for abandoned
  attempts, so a pending row lives until someone retries or cancels it.
