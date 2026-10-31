# ca-008 — cart-svc: cart.updated through a transactional outbox (done, 2026-10-30)

## What

`cart-svc` "published" `cart.updated` by calling `NoopEventBus.publish`, which wrote a `debug`
log line and returned. Every cart mutation was therefore silent, after commit, and with no way
to recover the event. This task deletes that bus and writes the event in the same transaction
as the mutation, through the shared `@ecom/messaging` relay built with au-004.

## How

- `cart-svc/db/003-cart-outbox.sql` — `cart.outbox`, same twelve columns and four CHECKs as
  `auth.outbox` (`aggregate_type IN ('cart')`, `event_type = 'cart.updated'`,
  `envelope->>'type' = event_type`, `envelope->>'id' = event_id::text`) plus
  `idx_outbox_pending (created_at) WHERE status = 'pending'`.
- `src/outbox/cart-outbox.ts` — `record(client, cart, items)` writes the envelope built from
  `buildCartUpdatedEvent(cart, items, computeTotals(items))`.
- `src/cart/cart.repository.ts`:
  - `findItems(cartId, client = getPool())` — one extra optional parameter, so the snapshot can be
    read with the mutation's own client; public call sites are unchanged.
  - a private `record(client, cart)` helper that reads the items and writes the row, used by every
    mutation; `ItemMutation` carries `items: CartItemRow[]`.
  - `convertActiveCart` is wrapped in `withTransaction`: `UPDATE … RETURNING` → `record` → `COMMIT`.
  - `CartRow.status` is the contract enum `CartStatus`, not `string`.
- `src/events/event-bus.ts` **deleted**; `cart.module.ts` drops the `EVENT_BUS` provider and adds
  `createOutboxModule({ schema: 'cart', producer: 'cart-svc', … })` + `CartOutbox`.
- `cart.service.ts` and `cart-merge.service.ts` lost `EVENT_BUS`, `Logger`, and `publishCartUpdated`;
  they compute totals from the items the repository returns instead of re-reading after commit.
- `cart.mapper.ts` — `buildCartUpdatedEvent` returns `CartUpdatedPayload` from `@ecom/contracts`,
  so the payload is provably the contract's type; the local interface is gone.
- Five e2e suites now assert on `cart.outbox` instead of an in-process spy, scoped by
  `aggregate_id = cartId` (`test/outbox.helpers.ts`) because vitest runs spec files in parallel
  against one database.

## Decisions

1. **The row goes in the mutation's transaction.** Exactly one event per committed mutation, and
   a rollback or a no-op writes none. Rejected: `NoopEventBus`, and any publish-after-commit,
   which cannot survive a crash between the commit and the send.
2. **Key by `cartId`.** The identity of a cart changes during merge (guest session → user), so a
   key on `userId`/`sessionId` would split one cart's history across two keys. Rejected: key by
   the acting identity, which is what `9.Testing.md` wrongly claimed before this task.
3. **Read the items with the transaction client.** The published payload must describe the state
   that committed; a post-commit read lets a concurrent mutation leak into an older event.
   Rejected: reuse the service's existing post-commit read, which is the bug this task exists for.
4. **`convertActiveCart` becomes transactional.** The internal convert route (ca-007) is the only
   path that publishes `status: 'converted'` *with* items, and a bare `UPDATE` cannot hold the
   snapshot it reports. Rejected: keep it bare and accept an event that can disagree with itself.
5. **No-ops record nothing, clears always record.** `updateItemQty` on a foreign item and
   `deleteItems` with `deletedCount = 0` return before `record`; a clear of an empty cart still
   touches `updated_at`, so it still emits. The rule is "one row per state change", not "one row
   per HTTP call".
6. **The envelope CHECKs are real constraints.** `envelope->>'type' = event_type` makes it
   impossible to insert a row whose envelope contradicts its columns. Rejected: rely on the
   TypeScript type alone, which does not survive a hand-written `INSERT`.
7. **The relay is the package's, not cart's.** Same lease, retry, and lock semantics as auth;
   cart contributes only the schema name, the producer string, and the payload builder.
   Rejected: keep the order-svc-shaped `OutboxService` (whose `dispatchEvent` only logs).

## Verification

| Check | Result |
|---|---|
| `cart-svc` `pnpm test` | 91 passed (14 files) |
| `cart-svc` `pnpm test:e2e` | 96 passed, 1 skipped (11 files; live spec skipped by default) |
| `cart-svc` `pnpm test:e2e` with `RUN_KAFKA_E2E=1` | 97 passed (11 files, live spec included) |
| `cart-svc` `pnpm lint` | 0 warnings, 0 errors (71 files) |
| `cart-svc` `tsc --noEmit --incremental false` | exit 0 |
| schema e2e | 7 tables alphabetically + `idx_outbox_pending` |
| outbox e2e (8 cases) | one row per committed mutation and one per merge; zero for a no-op, a rejected mutation, an empty delete and a replayed merge; payload `items`/`totals` equal the HTTP response; publish in `created_at` order keyed by `cartId`; retry, `failed` at 5, `skipped` under a held lock |
| rewired suites | `cart`, `cart-merge`, `internal`, `cart-security`, `wishlist` all read `cart.outbox`; the merge-replay, no-op and rejected-mutation assertions were preserved one-for-one |
| live proof (`RUN_KAFKA_E2E=1`) | one record on `cart.updated`, `key = cartId`, `parseEventEnvelope` passes, payload deep-equals the stored row, row `published` |
| commit | `cart-svc` `a87bde4` |

## Open

- Committed on 2026-10-31 as `a87bde4`. The gate re-run that day was lint (0/0, 71 files), 91
  unit tests in 14 files and `nest build`; e2e was **not** re-run because the compose stack was
  down, so the 96 + 1 skipped above is the 2026-10-30 run. Seven `e2e-run*.log` debug artifacts
  from that session were deleted rather than committed.
- ca-009 deletes `POST /cart/internal/carts/:userId/convert` and its spec once the `order.created`
  consumer is green.
- The payload carries every cart item, so a very large cart approaches the 1 MB Kafka default;
  shrinking it is a contract change, not a cart change.
- Outbox retention/archival is unplanned; `cart.outbox` grows one row per mutation.
- `cart-security.e2e-spec.ts` had no event assertion to convert, so one was **added** ("no outbox
  row for a rejected mutation") rather than rewritten — the suite is stronger than before.
- `MergeResult` exposes `cart` + `merged`, not `items`; the merge service reads the payload from
  the repository's returned item array instead.
