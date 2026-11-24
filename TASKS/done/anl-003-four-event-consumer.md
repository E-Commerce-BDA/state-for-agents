# anl-003 — consume four domain events into analytics facts (done, 2026-11-24)

- Repos: `analytics-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: kafka-consumer
- Started: 2026-11-24 | Finished: 2026-11-24

## What

analytics-svc had HTTP beacon ingest and a Mongo outbox but no Kafka consumer,
so cart, order and registration events never became funnel facts. Added one
consumer on the group exactly `analytics-svc`, with four `@EventPattern` routes
on the shared Nest transport: `cart.updated`, `order.created`, `page.viewed`
and `user.registered`.

Each fact is written with its `processed_events` claim in one Mongo transaction.
Added `order_events` and `user_events` at 60d TTL beside the existing
`page_views` (30d) and `cart_events` (60d); `processed_events` keeps no TTL.

## Why

Messaging's `ProcessedEventsStore` is SQL-only, so analytics claims an event by
inserting `_id: eventId` into `processed_events`. A duplicate key means a
redelivery is already applied; any other error propagates so the record is
retried. The claim and the fact share a transaction, so a crash cannot leave an
event marked done without its fact.

Rejected: adding a Mongo store to `@ecom/messaging` as 0.6.0 - a package
version, tarball and repin of every consumer for a capability only analytics
needs. Rejected: folding orders into `cart_events`, which would blur two funnel
stages. Rejected: a group per topic or an unbounded ladder.

## How

- `src/consumer/fact-store.ts`: Mongo claim + fact insert under
  `MongoTransactions`.
- `src/consumer/handlers.ts`: four payload parsers writing only the fields a
  funnel needs; no display name or email in the user fact.
- `src/consumer/{analytics-consumer.controller,consumer-runtime,events.module}.ts`:
  four routes, one group, `retryBudgetMs: 20_000`, `KAFKA_CONSUMER_ENABLED`.
- `app.module.ts` and `main.ts` wire the module and start the consumer without
  awaiting it; e2e suites set the flag false.
- Added `@nestjs/microservices` to the service deps.
- Commits: `3f1d415` (service), `5874907` (Documentation).

## Verification

- `npx tsc --noEmit` exit 0.
- `pnpm test`: 9 files / 33 tests passed (up from 8 / 20).
- `pnpm lint` and `pnpm build` exit 0.
- `pnpm test:e2e` not run: needs the live Mongo replica set and Kafka.

## Follow-ups

- `anl-004` can build the idle-cart detector on these facts.
- Move the claim into `@ecom/messaging` if a second Mongo consumer appears.
