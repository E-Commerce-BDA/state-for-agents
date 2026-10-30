# cat-009 — consume `order.created` and commit the reservation

- Repo: `catalog-svc` (+ `Documentation`)
- Phase: P3 · priority: P0 · kind: bug · transport: kafka-consumer
- Started: 2026-10-30 · Finished: 2026-10-30

## What the defect was

`POST /catalog/internal/stock/commit` worked, but **nothing called it in
production**. `order-svc` writes `order.created` to `order.outbox` inside TX2 and the
relay only logs (`OutboxService.dispatchEvent`), and catalog-svc had no Kafka
consumer at all. So a real checkout went:

1. `POST /checkout` → catalog reserved the stock (`held`, `products.stock`
   decremented once, a `sale` movement written).
2. The order was created and paid. Nobody told catalog.
3. After 900 s the sweep released the hold: stock restored, `cancel` movement
   written.

The unit was back on the shelf while a paid order for it existed — the double sell
`STATUS.md` called the highest-risk open item. The commit endpoint was not the bug;
the missing consumer was.

## How it was fixed

### Schema and the claim invariant

`db/006-order-created-consumer.sql` adds `catalog.processed_events`
(`event_id` PK, `topic`, `processed_at`, index on `processed_at`). The invariant is
stated in the file header and enforced by the code: **a row exists only if the side
effect was applied**. The claim is inserted inside the same transaction as the
commit, so a terminal-but-unapplied outcome rolls the claim back and the DLQ stays
the only record of a failed event.

### Repository: one transaction, two writers

`StockReservationsRepository` gained:

- `withTransaction(fn)` — BEGIN/COMMIT/ROLLBACK, rethrows the caller's error, and
  swallows a failing ROLLBACK so a lost connection cannot mask the real reason;
- `markProcessed(client, eventId, topic)` — `ON CONFLICT (event_id) DO NOTHING
  RETURNING event_id` → `rowCount > 0`;
- `commitInTransaction(client, reservationId, orderId)` — the old `commit()` body
  minus the transaction. No stock write and no movement row: stock was decremented
  and a `sale` movement written when the hold was taken.

`commit()` is now `withTransaction(c => commitInTransaction(...))`, so
`POST /internal/stock/commit`, its e2e and its service spec are unchanged.

Two error classes (`ReservationClosedError`, `ReservationMismatchError`) extend
`ConflictException`, so the HTTP route keeps answering `409 RESERVATION_CLOSED`
through the existing filter while the consumer can tell terminal from retryable with
`instanceof`.

### Handler: classify, then write

`OrderCreatedHandler.handle(raw)` is pure until the last step:

1. `readEventEnvelope` — normalizes the legacy `topic`/`eventType` dual-write;
   failure ⇒ `invalid(envelope)`.
2. `type !== 'order.created'` ⇒ `ignored(not-subscribed)` (defensive; one topic is
   subscribed).
3. `parseEventPayload` ⇒ `invalid(payload)` with a 3-issue / 300-char Zod summary.
4. `reservationId === ''` ⇒ `ignored(no-reservation)` and **no transaction** — the
   contract allows `''` for a resumed legacy order, there is nothing to commit.
5. Otherwise one transaction: claim the event id, then commit the hold.

### Consumer: manual commit, named DLQ reasons

`KafkaOrderConsumer` copies the search-svc shape (raw `kafkajs`,
`groupId`/`clientId` `catalog-svc`, `autoCommit: false`, `fromBeginning: false`,
`NODE_ENV=test` opt-out, 5 s reconnect, `KAFKA_CONSUMER_ENABLED=false` opt-out) and
narrows it to a **route table** keyed by topic, so `cat-010` adds a key instead of a
second consumer (two consumers in one group would split partitions).

| Input | Retry | DLQ reason | Offset |
|---|---|---|---|
| body not JSON | none | `invalid-json` + `rawValue` | after the write |
| envelope invalid | none | `invalid-envelope` | after the write |
| payload invalid | none | `invalid-payload` | after the write |
| `reservationId: ''` | n/a | — (ignored) | commit |
| event id already processed | n/a | — (duplicate) | commit |
| hold `released`/`expired` | none | `reservation-closed` | after the write |
| hold belongs to another order | none | `reservation-mismatch` | after the write |
| hold not found | 1/2/4/8/16 s | `reservation-missing` | after the write |
| anything else (DB down) | 1/2/4/8/16 s | `transient-exhausted` | after the write |

Counters `{ committed, duplicate, ignored, invalid, dlq }` are process-local and
exposed on `GET /catalog/internal/consumer-stats` behind `ServiceKeyGuard`.

## Decisions

| Decision | Why | Rejected alternative |
|---|---|---|
| `processed_events` claimed in the same transaction as the commit | The only way "applied once" is true after a crash between the two writes | Claim first, then commit (a crash in between silently drops the event) |
| Terminal outcomes throw instead of returning a branch | The rollback *is* the invariant: no claim row, DLQ is the record | Return `closed` and commit the claim (records success for work that never happened) |
| `ReservationClosedError`/`Mismatch` extend `ConflictException` | Keeps the existing HTTP 409 contract without a mapping layer | Plain `Error` + a try/catch in the service |
| A commit request without an `orderId` is not a mismatch | Preserves the HTTP contract: a bare replay cannot prove disagreement. An event always carries one and is checked | Treat `null` vs stored as a mismatch (breaks `POST /stock/commit` replays) |
| `commitInTransaction` returns `{ outcome, reservationId, orderId }` rather than the bare union in the plan | The HTTP route needs the stored `order_id` for its response and the handler needs `already-committed`; a second query to get either is waste | Re-select after commit |
| Raw `kafkajs`, no `@nestjs/microservices` | Matches search-svc, keeps `srch-002` a migration rather than a prerequisite | Add the transport before the migration that owns it |
| Route table in the consumer | `cat-010` is one key, not a second consumer/group split | A consumer per topic |

## Verification

- `pnpm exec tsc --noEmit` → 0 errors
- `pnpm lint` → 0 warnings, 0 errors (118 files)
- `pnpm test` → 22 files, 125 tests (11 handler, 13 consumer)
- `pnpm test:e2e` → 9 files, 88 tests (8 new consumer e2e, 21 schema tests)
- `pnpm build` → 0

E2E proves the acceptance criteria directly: the hold becomes `committed` with
`order_id` stored, `products.stock` is unchanged, **no new `stock_movements` row**
appears, the first event commits and the second with the same id is a `duplicate`,
a new id for a committed hold is a no-op (`already-committed`), a released hold
throws `ReservationClosedError` **and leaves no `processed_events` row**, and an
unknown hold throws `404` so the consumer can retry.

## Two pre-existing defects found by the gate

1. **`node_modules` was on `@ecom/contracts` 1.1.0** while `package.json` pinned the
   1.7.0 tarball, so `readEventEnvelope`/`parseEventPayload` did not exist for
   catalog. `pnpm install --ignore-workspace` (the root workspace excludes
   `catalog-svc/**`) fixed the lockfile; committed as `chore(deps)`.
2. **`tsc` and `nest build` were red on `master`** with 12 errors in
   `badges`/`products`: the `product.updated` call sites read `product.category?.id`,
   `product.brand?.id` and `product.updatedAt`, but `findById` is `SELECT *` and
   `ProductRow` has `category_id`/`brand_id`/`updated_at`; `products.repository.ts`
   also referenced `ProductBadgeItem` without importing it, and `ProductBadgeRow`
   lacked the `id` the join selects. Repaired in its own commit (`fix(catalog)`) —
   the cat-009 gate cannot be green over a build that does not compile.

## Open

- **Correct but inert until `ord-011`.** The outbox relay still only logs, so no
  `order.created` reaches Kafka in a real deployment. Until then the double sell
  persists and this task is a prerequisite, not a fix.
- The 900 s TTL is the clock. An event that arrives after the sweep wins is
  `reservation-closed` in the DLQ and the stock is already back on the shelf: a
  reconciliation incident, not something a retry can repair.
- `catalog.processed_events` grows without bound. Retention is a seam (the
  `processed_at` index) with no sweeper yet.
- `cat-010` (`order.status.updated` → release) and `cat-008` (`product.imported`)
  remain out of scope.
- **`ord-012` was re-scoped, not implemented** (second half of this session). Its
  stored rationale — "the bridge targets a non-existent endpoint, so it never
  works" — was stale: `CartClient.convertCart` does reach a live, service-key
  guarded `POST /cart/internal/carts/:userId/convert`. What is wrong is the
  *coupling*: a fire-and-forget call inside the checkout request that swallows
  its own failure. It cannot be deleted yet — the relay only logs and cart-svc has
  no consumer, so removing the call means **zero** conversions instead of a
  best-effort one. `ord-012` is now `P3` with `dependsOn: ["ca-009","ord-011"]`,
  and the split is written into both tasks: `ca-009` deletes the cart-svc
  endpoint once its consumer is green, `ord-012` deletes the call site.
