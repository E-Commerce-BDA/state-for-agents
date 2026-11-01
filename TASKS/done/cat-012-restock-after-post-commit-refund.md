# cat-012 — restock a committed hold after a post-commit refund (done, 2026-11-01)

## What

`cat-010` deliberately refused to release a **committed** hold on any release
status: the stock had already been decremented when the hold was committed, so
restoring it would put a sold unit back on the shelf and let a second customer buy
it. That is right for a cancellation or a failure of an order that shipped. It is
wrong for a **refund** — the one transition where the customer hands the unit back
and the units genuinely should return. Before this task a `refunded`
`order.status.updated` against a committed hold was logged as the `not-releasable`
anomaly and the units never came back, leaving a refunded item unsellable until an
operator adjusted stock by hand.

`cat-012` closes that seam. A `refunded` status event whose reservation is
`committed` restocks **exactly once**, records the movement under the dedicated
`return` reason (never `cancel`), and lands the hold on a new terminal `refunded`
state, so the ledger can tell a restock-after-sale apart from a pre-sale
cancellation. A duplicate refund is a no-op, and `cat-010`'s held-release path is
untouched.

## How

- `catalog-svc/db/009-refund-restock-status.sql` (new) — widens
  `stock_reservations_status_check` to add `'refunded'`. `stock_movements.reason`
  already allowed `'return'` (legal since `001`), so no ledger migration was needed.
  Applied to `ecom-pg` before the e2e gate.
- `catalog-svc/src/stock/stock.types.ts` — `'refunded'` added to `ReservationStatus`
  and to `isTerminal`; new `RestockOutcome` union (`restocked` / `already-restocked`
  / `not-refundable`); `ReleaseOutcome.already-released` widened to accept a
  `'refunded'` status, because a cancelled event can now arrive for a hold that a
  refund already settled.
- `catalog-svc/src/stock/stock-reservations.repository.ts` — `restore()` and
  `recordMovement()` gained a `reason` parameter (`restore` defaults to `'cancel'`,
  so the `cat-010` release path is byte-for-byte unchanged); new
  `restockRefundInTransaction(client, id)` mirrors `releaseInTransaction`'s
  report-don't-throw contract: `committed` → restore each item with `'return'` and
  set `'refunded'`; `refunded` → `already-restocked`; anything else →
  `not-refundable`.
- `catalog-svc/src/events/order-status-updated/order-status-updated.handler.ts` — a
  branch keyed on `payload.to === 'refunded' && reservation.status ∈ {committed,
  refunded}` routed to `restockRefundInTransaction`, returning a new `restocked`
  outcome variant; committed + cancelled/failed still falls through to the release
  path and reports the `not-releasable` anomaly.
- `catalog-svc/src/events/handler-outcome.ts` — `toOrderStatusUpdatedOutcome` maps
  `restocked` to `{ kind: 'applied' }` with its own log line, and the stale
  "(cat-012)" TODO marker on the anomaly warn is rewritten now that the decision is
  made rather than deferred.
- Tests: `order-status-updated.handler.spec.ts` (12 cases — the committed-refund
  test rewritten into restock + still-refuses-cancel + already-restocked no-op) and
  `test/order-status-updated.e2e-spec.ts` (10 cases — restock-once, replay
  `duplicate`, fresh-event-id `already-restocked`, and committed-cancel anomaly).

## Decisions (+ one rejected alternative each)

1. **A new terminal `refunded` status, not a reuse of `released`.** `released` means
   "the hold was cancelled before the sale"; folding a restock-after-sale into it
   would make the movement ledger (`return`) and the hold row disagree about what
   happened. Rejected: reuse `released` — it hides refund volume inside cancellations
   and breaks the audit trail `cat-012`'s own key decision demanded.
2. **A dedicated `return` movement reason.** The reason already existed in the
   `001` CHECK but was never written by the reservation lifecycle. Rejected: emit
   `cancel` — `cat-012`'s stored rationale was explicitly that `cancel` would
   misreport why the stock came back.
3. **Restock is keyed on the refund status alone, not on the reservation being
   committed for any release status.** A committed hold whose order was merely
   cancelled or failed is not a refund and must not restock (double-sell). Rejected:
   branch only on `status === 'committed'` — it would restock on a cancellation too.
4. **The `refunded` status is the idempotency backstop, not just
   `processed_events`.** The claim dedupes the *same* event id; a redelivered refund
   carrying a *new* id would pass the claim and hit a hold already settled. Rejected:
   rely on `processed_events` alone — it cannot see across distinct event ids for the
   same order.
5. **`held` + `refunded` keeps the `cat-010` release path (a `cancel` movement).** A
   hold that never committed was never sold, so a refund of it is a pre-sale release,
   not a restock-after-sale. Rejected: route every refund through
   `restockRefundInTransaction` — it would relabel a never-sold cancellation as a
   return and change `cat-010`'s verified behavior (acceptance criterion 4).

## Verification

| Check | Result |
|---|---|
| `catalog-svc` `pnpm exec tsc --noEmit -p tsconfig.json` | exit 0 (src + test) |
| `catalog-svc` `pnpm test` | 159 passed (24 files) |
| `catalog-svc` `order-status-updated.handler.spec.ts` | 12 cases: committed + refund restocks once and skips the release path; committed + cancel stays `not-releasable`; refund on an already-`refunded` hold is `already-restocked`; held + cancel/fail/refund still release |
| `catalog-svc` `pnpm test:e2e` | 120 passed, 5 skipped (12 files, 2 live-Kafka gated) |
| `catalog-svc` `test/order-status-updated.e2e-spec.ts` | 10 cases incl. restock returns stock to the pre-sale figure with a `return` movement + `refunded` hold, same-event-id replay is `duplicate` (no second restock), fresh-id repeat is `already-restocked`, committed-cancel does not restock |
| `catalog-svc` `pnpm lint` | 0 warnings, 0 errors (133 files) |
| `catalog-svc` `pnpm build` | clean; `restockRefundInTransaction` present in `dist/src/stock/stock-reservations.repository.js` |
| migration | `db/009-refund-restock-status.sql` applied to `ecom-pg`; `stock_reservations_status_check` now admits `refunded` |
| commit | `catalog-svc` `6cc6182` (7 files, +313/−22), local-only |
