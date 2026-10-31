# cat-007 — catalog-svc: product.updated and category.updated through an outbox (done, 2026-10-31)

## What

catalog-svc published `product.updated` and `category.updated` through an in-process
`IEventBus` whose Kafka implementation logs and swallows a broker failure, so a committed
product change could leave no event behind and nothing recorded that it had been attempted.
This task replaces that path with `catalog.outbox`: every mutating service method now runs
inside `withTransaction`, writes the row and the outbox row with the same `PoolClient`, and a
relay from `@ecom/messaging` 0.2.0 publishes the stored envelope afterwards. The producer
side of the event bus (`IEventBus`, `KafkaEventBus`, `InMemoryEventBus`, `EventsService`) is
deleted; the Kafka **consumer** path (`KafkaOrderConsumer`, `OrderCreatedHandler`) is
untouched. Coverage also grew: variant, option, image and discount mutations emit
`product.updated` now, which they never did.

## How

- `db/007-catalog-outbox.sql` — `catalog.outbox` mirroring `auth-svc/db/003-auth-outbox.sql`:
  `envelope jsonb NOT NULL`, `locked_until`, `last_error`, `idx_outbox_pending (created_at)
  WHERE status = 'pending'`, plus four consistency constraints: `aggregate_type IN
  ('product','category')`, `event_type IN ('product.updated','category.updated')`,
  `envelope->>'type' = event_type`, `envelope->>'id' = event_id::text`, and
  `envelope->'payload'->>(productId|categoryId) = aggregate_id::text`.
- `src/db/tx.ts` — `withTransaction<T>(fn: (client: PoolClient) => Promise<T>)`, copied from
  cart-svc (`BEGIN` / `COMMIT` / `ROLLBACK` / `release`).
- `src/outbox/catalog-outbox.ts` (+ `catalog-outbox.module.ts`) — `CatalogOutbox` injecting
  `OUTBOX_STORE`: `recordProduct(client, product)` and `recordCategory(client, category)`.
  Payload assembly moved here verbatim from `events.service.ts` / `products.service.ts`, so
  `store.write`'s contract validation runs inside the transaction. `occurredAt` comes from the
  row's own `updated_at` / `updatedAt`, not from wall clock, so a replay reproduces the
  original envelope. `ProductDetail | ProductRow` is discriminated by `'category' in product`.
- `src/products/products.repository.ts` — mutating methods and their read helpers grew
  `client?: Queryable`; the body is `const q = client ?? getPool();`. No behaviour change when
  the argument is omitted.
- `src/products/products.service.ts` (4 write sites), `src/categories/categories.service.ts`
  (3), `src/badges/badges.service.ts` (1, `assignProductBadges`) — each mutation is
  `withTransaction(async (client) => { const row = await repo.x(..., client); await
  this.outbox.recordProduct(client, row); return row; })`. Delete paths read the product
  inside the transaction before deleting, so the payload matches what committed.
- `src/events/` — `event-bus/{event-bus.interface,kafka-event-bus,in-memory-event-bus}.ts` and
  `events/events.service{,.spec}.ts` deleted; `events.module.ts` keeps `ConsumerMetrics`,
  `ConsumerStatsController`, `OrderCreatedHandler`, `KafkaOrderConsumer`.
- `src/app.module.ts` — `createOutboxModule({ schema: 'catalog', producer: 'catalog-svc',
  clientId: 'catalog-svc', pool: getPool })`.
- Deps: `@ecom/contracts` → 1.8.0 tarball, `@ecom/messaging` → 0.2.0 tarball,
  `pnpm install --ignore-workspace`.
- Tests: `test/outbox.e2e-spec.ts` + `test/outbox.helpers.ts` (aggregate-scoped drains, since
  every e2e suite shares one database), `test/live-kafka.e2e-spec.ts` (gated on
  `RUN_KAFKA_E2E=1`), and the unit specs switched from a bus spy to a fake `OUTBOX_STORE`.

## Decisions

1. **A transaction per mutation, not a transaction per request.** Only the methods that must
   move the row and the event together got a client; reads keep using the pool. Rejected: wrap
   the controller, which would hold a connection across validation and mapping for no benefit.
2. **Payload assembly in `CatalogOutbox`, not in the services.** `store.write` validates
   against the contracts schema, so keeping the builder next to the write is what makes a
   drifted payload abort the mutation. Rejected: build the payload in the service and pass a
   finished object, which lets a service construct something the outbox never checks.
3. **`occurredAt` from the row, not `new Date()`.** A replayed or late-published envelope then
   describes when the change happened. Rejected: publish time, which makes the same row produce
   two different events depending on when the relay ran.
4. **Delete the producer bus instead of leaving it wired.** After cat-007 nothing in catalog
   publishes through it, and a second unpersisted publish path is exactly the drift this task
   removes. Rejected: keep it "for later". Cost: the consumer-side files had to be separated
   from the same module, and two specs deleted with it.
5. **One `product.updated` for variant/option/image/discount changes.** These all make a cached
   product card stale; the existing payload already carries `images`, so no contract change was
   needed. Rejected: add `variants`/`discounts` to `productUpdatedPayloadSchema` — that is a
   contracts release plus a search-svc mapper change (D11 in the plan).
6. **Aggregate-scoped drains in e2e.** Every suite shares one database, so an unscoped
   `drainOnce()` would claim another suite's rows and publish them to the recording publisher.
   Rejected: a per-suite schema, which the repo does not do anywhere.

## Verification

| Check | Result |
|---|---|
| `pnpm build` | exit 0 |
| `pnpm lint` | 0 warnings / 0 errors (119 files) |
| `pnpm test` | 125 passed |
| `pnpm test:e2e` (relay disabled) | 96 passed, 2 skipped |
| `test/outbox.e2e-spec.ts` | create → one pending `catalog.outbox` row with `envelope.type = 'product.updated'`; drain via `OUTBOX_RELAY.drainOnce()` → `published`; variant and discount mutations each produce a row; a forced failure after the outbox write leaves no product row and no outbox row |
| `RUN_KAFKA_E2E=1 pnpm test:e2e -- test/live-kafka.e2e-spec.ts` | 2/2 — `product.updated` and `category.updated` consumed from the real broker, matching on the `x-event-id` header |
| `kafka-console-consumer` (in `ecom-kafka`) | one record on each topic with `producer: catalog-svc`, key = aggregate id, `parseEventEnvelope` accepted |
| `@ecom/contracts` / `@ecom/messaging` in `node_modules` | 1.8.0 / 0.2.0 |
| commit | `catalog-svc` `7b081ea` |

## Open

- Committed on 2026-10-31 as `7b081ea`. The gate re-run that day was lint (0/0, 119 files), 125
  unit tests in 21 files and `nest build`; e2e was **not** re-run because the compose stack was
  down, so the 96 + 2 skipped above is the 2026-10-31 run.
- `catalog.outbox` has no retention sweep and no metrics endpoint (failed count, oldest pending
  age). Same gap as `auth.outbox` and `cart.outbox`.
- The `CHECK` on `aggregate_type` means a future third aggregate (say `brand.updated`) needs a
  migration, not just code.
- `src/events/event-bus/` remains on disk as an empty directory.
- `cat-010` (`order.status.updated` consumer) and `cat-008` (`product.imported`) are unaffected
  by this change but still todo.
