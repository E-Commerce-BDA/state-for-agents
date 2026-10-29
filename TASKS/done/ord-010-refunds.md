# ord-010 — order-svc: real refunds and canonical `order.status.updated`

## What

`refundOrder` only flipped rows: `orders → refunded`, `payments → refunded`, a
history entry and a `refundOrder.refunded`-style `order.refunded` event. No
provider was called, so the books could claim a refund the customer never
received, there was no record of *which* capture was reversed or what the
provider answered, and the lifecycle had two event vocabularies
(`fromStatus`/`toStatus` on the status path, a separate `order.refunded`).

A refund is now a ledger entry with the provider in the middle:

```
existing refund?  succeeded → return it   pending → 409 REFUND_IN_PROGRESS
                  failed    → retry in place with the reserved amount
captured payment (status='captured', transaction_id NOT NULL) → else 409 NO_CAPTURED_PAYMENT
INSERT refunds (pending)                          ← UNIQUE(order_id) reserves the slot
processRefund(transaction_id, amount, reason)
 success → TX: refunds→succeeded + provider_reference, payments→refunded,
               orders→refunded/refunded, history, outbox order.status.updated
 failure → refunds→failed + failure_reason, order and payment untouched, 502
```

## How

- `db/005-order-refunds.sql` — the `refunds` table (`UNIQUE (order_id)`,
  `CHECK (amount > 0)`, `status IN ('pending','succeeded','failed')`),
  `idx_refunds_order`, and `trg_refunds_updated_at`.
- `src/db/rows.ts` — `RefundStatus`, `RefundRow`.
- `src/orders/refunds.repository.ts` — `findByOrderId`, `findCapturedPayment`,
  `startRefund` (`ON CONFLICT DO NOTHING`, returns `created: false` for the
  loser), `markSucceeded` (one transaction: ledger, payment, order, history,
  outbox), `markFailed` (ledger only).
- `src/orders/orders.service.ts` — the flow above; `refundInProgress()`.
- `src/orders/orders.repository.ts` — `order.status.updated` payload keys become
  `from`/`to`; `refundOrderWithHistory` deleted.
- `src/orders/orders.controller.ts` — `POST :id/refund` returns
  `{ order, refund }` so the caller sees the provider reference.
- `src/orders/orders.module.ts` — provides `RefundsRepository`, imports
  `PaymentsModule`.
- Tests: `orders.service.spec.ts` (refund block rewritten against a
  `RefundsRepository` mock, 24 cases), `orders.e2e-spec.ts` (22 cases, a
  `MockPaymentProvider` spy), `schema.e2e-spec.ts` (applies every `db/*.sql` in
  order, asserts 8 tables and the refund unique constraint).

## Decisions (+ one rejected alternative each)

- **The ledger row is reserved before the provider call and settled after it.**
  Two transactions around the network call; a single transaction would hold a
  row lock across a third-party request. Rejected: call the provider and write
  the ledger afterwards — a crash in between leaves money moved with no record.
- **`UNIQUE (order_id)` is the idempotency gate**, not a Redis lock. The second
  concurrent request loses the insert and reads the winner's row, so concurrency
  is settled by the database and survives a Redis outage. Rejected: `idem:` key
  + lock on the refund route (a second cache to keep honest for a write that is
  already serialised by the unique index).
- **A provider failure is a ledger fact, not an error that vanishes.** A thrown
  call is persisted as `failure_reason` before the 502, because an
  unauditable failed refund cannot be reconciled. Rejected: `markFailed` only on
  a declined answer and let an exception bubble untouched.
- **`payments.status` moves to `refunded` only on success**, so a failed refund
  leaves the payment `captured` and a retry is possible. Rejected: mark the
  payment refunded optimistically (the books would lie about money that never
  moved).
- **The retry reuses the reserved amount and reason.** A provider outage must
  not change what the customer gets back, so the DTO's `amount` is ignored once
  the row exists. Rejected: re-read the DTO on retry.
- **`from` is read with `SELECT … FOR UPDATE` inside the settlement
  transaction.** The event must report the transition it actually performed.
  Rejected: trust the status loaded before the provider call — a concurrent
  `delivered → cancelled` would make the event lie.
- **The amount check still precedes the FSM check**, so `400` keeps its existing
  message and the refundable-state error stays a `400` (unchanged API). Rejected:
  reorder to FSM-first, which would change the status an over-amount request sees.
- **One event family.** `order.status.updated {from, to, …}` carries
  `refundAmount`/`refundReference` for refunds; `order.refunded` is deleted.
  Rejected: keep the second event and teach consumers two shapes.
- **E2E asserts the "no `order.refunded`" rule scoped to the order under test.**
  The suite shares one database with earlier runs, so a global `COUNT(*) = 0`
  would assert on history instead of on this refund. Rejected: truncating the
  outbox in `beforeAll` (it would break the relay-worker test's premise).
- **The provider fake is a `vi.spyOn` on the running `MockPaymentProvider`, not
  a second app with `overrideProvider`.** It asserts call count and arguments
  without a second Nest instance sharing the pool. Rejected: the two-app
  pattern used for the Redis-down drill (needed there because the failure is at
  startup, not per call).

## Verification

All commands from `order-svc` on 2026-10-30:

| Gate | Result |
|---|---|
| `pnpm lint` (oxlint --type-aware) | 70 files, 0 warnings, 0 errors |
| `pnpm test` | 6 files / 77 tests (`orders.service` 24, `checkout.service` 25) |
| `pnpm test:e2e` | 6 files / 76 passed, 1 skipped (live catalog) |
| `pnpm build` (`nest build`) | exit 0 |
| `psql` shape check | `db/005` applied by `schema.e2e-spec.ts`; `refunds` present with its UNIQUE constraint and `idx_refunds_order` |

Behaviour proven by `test/orders.e2e-spec.ts` (real Postgres):

1. refund on a delivered order → the provider is called **once** with the
   stored `transaction_id` and the grand total; the response carries the ledger
   row with `status='succeeded'` and a `mock_ref_` reference; `payments.status`
   is `refunded`; the order is `refunded`/`refunded`; the outbox holds
   `order.status.updated` with `from='delivered'`, `to='refunded'`,
   `refundAmount='118.00'`, `actor=admin`;
2. replaying the same refund → `200`, the same row, **no** provider call;
3. provider refusal → `502 REFUND_PROVIDER_FAILED`, `refunds.status='failed'`
   with the reason, order still `delivered`, payment still `captured`;
4. retrying that refund → `200`, same ledger row id, provider called once with
   the reserved amount and the original reason;
5. a delivered order whose payment was never captured → `409
   NO_CAPTURED_PAYMENT` and no provider call; `403` for a customer and `400` for
   an over-amount request still hold.

Unit coverage adds the concurrent-loser (`created: false`) path, the in-flight
`409 REFUND_IN_PROGRESS`, the two provider-failure shapes, and the assertion
that `markSucceeded` receives the provider reference.

Commits: `e5878e7` refunds ledger · `0b1642e` provider call + settlement ·
`9d3cdbd` canonical payload · `059d92f` unit + e2e coverage.
Docs: `Documentation` `ca295ab` (API) · `9324d3b` (DB) · `acde1da` (order.md).

## Follow-ups

- `UNIQUE (order_id)` locks v1 to **one** refund per order; a second partial
  refund is rejected. Relaxing it needs a running refunded total and a
  `(order_id, requested_at)` history, which is a schema change of its own.
- A refund stuck in `pending` (a crash between `startRefund` and
  `markSucceeded`) has no sweeper: it answers `409 REFUND_IN_PROGRESS` until an
  operator marks it failed. Same class of gap as the stale pending payments
  (`ord-011`).
- Only `delivered → refunded` is allowed, so an admin cannot refund a
  `confirmed`/`processing` order (cancellation goodwill). That needs a decision
  on whether an unshipped refund reverses the payment or voids the capture.
- If the provider succeeds and the settlement transaction then dies, the
  provider reference is lost. Reconciling from the provider's refund list is out
  of scope for v1 and should be part of the reconciliation task.
