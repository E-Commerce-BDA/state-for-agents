# cat-010 — release stock when an order is cancelled, failed or refunded (done, 2026-11-01)

## What

The only release path was a best-effort HTTP call: `orders.service.ts` POSTs
`/internal/stock/release` when an order reaches a terminal state, and a catalog that is
down at that moment leaves the hold `held` until the 900 s sweep — the unit stays
unsellable while the customer's money was already returned. `order.status.updated` is
the durable version of the same intent, and it was already being published.

cat-010 adds that topic to the catalog consumer and releases the reservation by order
id inside the same transaction as the `processed_events` claim. A redelivery is a
no-op, a forward transition releases nothing, and a *committed* hold is a logged
anomaly rather than a dead letter, because its stock was sold.

The premise the handler stands on did not exist yet: nothing wrote
`catalog.stock_reservations.order_id` while the hold was still `held` — it was set at
commit, i.e. after the order was confirmed. That fix landed in order-svc as part of
this task (`f7ad466`).

## How

- `catalog-svc/src/events/catalog-topics.ts` — `'order.status.updated'` added to
  `CATALOG_CONSUMER_TOPICS`. Same controller, same group: the file's own comment
  already explains why a second group is not an option.
- `catalog-svc/src/stock/stock.types.ts` — `ReleaseOutcome`
  (`released` / `already-released` / `not-releasable`) next to the existing types, so
  the transaction body can report instead of throw.
- `catalog-svc/src/stock/stock-reservations.repository.ts` — the body of `release()`
  moved into `releaseInTransaction(client, id)` (returns `null` for "no such
  reservation"), plus `findByOrderIdForUpdate(client, orderId)`. `release()` is now a
  thin wrapper that maps `null` → `NotFoundException` and `not-releasable` →
  `ConflictException('RESERVATION_CLOSED')`, so `POST /internal/stock/release` behaves
  exactly as before.
- `catalog-svc/src/events/order-status-updated/order-status-updated.handler.ts` (new,
  183 lines) — envelope → `parseEventPayload('order.status.updated', …)` →
  `RELEASE_STATUSES = {cancelled, failed, refunded}` → one transaction:
  `markProcessed` (false ⇒ `duplicate`), `findByOrderIdForUpdate` (none ⇒
  `ignored/no-reservation`), `releaseInTransaction`. Outcome union with
  `describe()`/`clip()` helpers copied from the `order.created` handler so a Zod error
  arrives on the DLQ record as one short line.
- `catalog-svc/src/events/handler-outcome.ts` — `toOrderStatusUpdatedOutcome`, with
  `counter: 'released'` on a real release and a `releaseLogger` warn for
  `not-releasable`.
- `catalog-svc/src/events/catalog-consumer.controller.ts` — `@EventPattern('order.status.updated')`
  with `@Payload() raw: string, @Ctx() ctx: unknown` (both decorators are load-bearing),
  registered next to the existing method.
- `catalog-svc/src/events/events.module.ts` — the new handler as a provider.
- `catalog-svc/src/events/order-created/order-created.handler.ts` — catches
  `ReservationClosedError` when the stored status is `released` and returns
  `{ kind: 'ignored', reason: 'released-by-cancellation' }`; `expired` and `mismatch`
  stay terminal.
- `order-svc/src/checkout/checkout.service.ts`, `checkout.repository.ts` — checkout
  generates the order id, sends it with the reserve call and writes the row under it
  (`COALESCE($18::uuid, gen_random_uuid())`), with a drift guard that throws if the
  written id differs from the one the hold names.
- Tests: `order-status-updated.handler.spec.ts` (227 lines),
  `catalog-consumer.controller.spec.ts` (+105), `order-created.handler.spec.ts`,
  `test/order-status-updated.e2e-spec.ts` (319 lines),
  `test/order-created.e2e-spec.ts`, `order-svc/test/checkout.e2e-spec.ts`.

## Decisions (+ one rejected alternative each)

1. **A committed hold is not released.** The stock was decremented when the reservation
   became `committed`; releasing it would put a sold unit back on the shelf and let a
   second customer buy it. Rejected: treat `committed` as releasable inside this
   handler — that is a double-sell, and the real requirement (restock after a
   post-delivery refund) needs its own movement reason, filed as `cat-012`.
2. **Find the reservation by `order_id`.** The event carries an order id and no
   reservation id, and `idx_stock_reservations_order` is a partial unique index, so at
   most one row can match. Rejected: restock by product id — it would touch whatever
   reservation else holds that product.
3. **Two release paths, one contract each.** `release()` keeps throwing for the HTTP
   route (404/409 are part of order-svc's saga); `releaseInTransaction` returns an
   outcome for the consumer. Rejected: reuse `release()` in the handler — a committed
   hold would dead-letter, which is exactly the case that deserves one warning line.
4. **`order.created` tolerates a cancellation-released hold.** The two topics give no
   cross-topic ordering, so a fast cancel is consumed before the commit; without this
   every cancelled order would leave a DLQ record. Rejected: ordering the two topics
   through one partition — they are already separate topics, so there is nothing left
   to order.
5. **One consumer group.** A second group for the new topic would split the partitions
   catalog already owns and double the dedupe bookkeeping. Rejected: a group per topic.
6. **The order id is planned by checkout, not assigned by the column default.** The hold
   has to name the order before the row exists, and patching it afterwards would be
   another best-effort call. Rejected: `UPDATE stock_reservations SET order_id` after
   the insert — it fails in exactly the crash window this task exists for.

## Verification

| Check | Result |
|---|---|
| `catalog-svc` `pnpm test` | 157 passed (24 files) |
| `catalog-svc` `order-status-updated.handler.spec.ts` | 11 cases: forward status ignored, cancel with no reservation ignored, cancel on `held` releases, cancel on `released` is a no-op, refunded on `committed` is `not-releasable`, duplicate short-circuits, malformed envelope/payload `invalid` with no transaction |
| `catalog-svc` `catalog-consumer.controller.spec.ts` | topic list includes `order.status.updated`; DLQ name resolves through the registry |
| `catalog-svc` `pnpm test:e2e` | 118 passed, 5 skipped (12 files passed, 2 skipped — both live Kafka suites are gated on `RUN_KAFKA_E2E`) |
| `catalog-svc` `test/order-status-updated.e2e-spec.ts` | 8 cases: hold → cancel restores stock exactly once, replay unchanged, shipped commits nothing, committed hold logs and stays committed |
| `catalog-svc` `test/order-created.e2e-spec.ts` | 8 cases, including cancellation-before-commit leaving no DLQ record |
| `catalog-svc` `pnpm lint` | 0 warnings, 0 errors (133 files) |
| `catalog-svc` `nest build` | clean |
| `order-svc` `pnpm test` / `pnpm test:e2e` | 75 unit (5 files) / 82 e2e passed (3 skipped) |
| commit | `catalog-svc` `0dcb9c9`, `order-svc` premise fix `f7ad466` |
