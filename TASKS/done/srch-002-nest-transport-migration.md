# srch-002 — search-svc consumes on the Nest Kafka transport (done, 2026-11-01)

## What

`srch-001` had already made the consumer correct: malformed records dead-lettered, invalid
payloads dead-lettered, `processed_events` claimed in the same transaction as the index upsert,
`search-svc` as the group. But it was the platform's own `kafkajs` run loop — a parser, a retry
ladder, a dead-letter producer and an offset commit, hand-written in `kafka-event-consumer.ts`.
catalog-svc had a second copy of that protocol (`cat-007`), and cart-svc was about to get a third
(`ca-009`).

`srch-002` deletes the copy. The four topics move to `@EventPattern` methods on one controller over
the Nest Kafka transport, and the protocol itself — parse, retry, dead-letter, count, commit — now
lives once, in `@ecom/messaging 0.3.0`.

search-svc went first (D7) because it was the safest proof: a heavily tested consumer whose
business logic was already correct, so any red test had to be the transport.

## How

- `src/events/search-consumer.controller.ts` (new) — `@EventPattern` for `product.updated`,
  `category.updated`, `blog.updated` and `product.imported`, each `@Payload() raw: string,
  @Ctx() ctx: unknown` → `KafkaEventHandler.run(ctx, topic, raw, …)`. `KafkaContext` and
  `@EventPattern` stay visible in this repo on purpose; hiding them behind the package's types
  would put the commit back somewhere a service can no longer read.
- `src/events/kafka-event-consumer.ts` + `kafka-event-consumer.spec.ts` (289 lines) — deleted.
  Every behavioural case was re-pointed, not dropped: the protocol cases at
  `ecom-messaging/test/consumer/kafka-event-handler.spec.ts`, the routing and DLQ-name cases at
  `test/search-consumer.controller.spec.ts` (11 cases) driving the real `KafkaDlqPublisher`, so
  `product.updated.dlq` and friends are still asserted end to end.
- `src/events/consumer-runtime.ts` (new) — `CONSUMER_GROUP_ID = 'search-svc'`,
  `createKafkaConsumerStrategy({ brokers, clientId, groupId })` (`postfixId: ''` inside), the
  `NestRelayLogger` adapter, and a `ConsumerRuntime` that owns the DLQ producer and the lag gauge.
  The gauge is started explicitly, never from `onModuleInit`, so a module built by a unit test
  opens no admin connection.
- `src/app.setup.ts` — `configureEventConsumer(app, config)`: `connectMicroservice` +
  `startAllMicroservices`, retried every 5 s, `KAFKA_CONSUMER_ENABLED` guard, `false` in the test
  env. Deliberately separate from `configureApp`, because every e2e suite calls `configureApp`
  alone and an HTTP test must never join a consumer group.
- `src/main.ts` — `void configureEventConsumer(…)` after `app.listen`. Not awaited: a broker that
  is restarting must not stop the API from answering.
- `src/events/consumer-metrics.ts` — the nine counters delegate to the package; `buildConsumerStats`
  adds `lag`, `totalLag`, `lastCommit`, `sampledAt`. `consumer-stats.controller.ts` takes
  `KafkaLagSampler` and returns the wider snapshot — additive, so a dashboard written against the
  old payload still works.
- `src/events/events.module.ts` — registers the controller, keeps `InMemoryEventConsumer` for
  `USE_IN_MEMORY_EVENTS` / `NODE_ENV=test`, drops the `EVENT_CONSUMER` / `KafkaEventConsumer`
  wiring.
- `vendor/ecom-contracts-1.9.0.tgz` replaces `1.7.0` in the same commit. This repo pins from
  `./vendor/`, and the strict payload schema makes `variants[]` a breaking change for anyone
  below 1.9.0 — so the repin has to land before any producer emits it (plan §Phase 1, D3).

## Decisions

1. **The transport swap changes no indexing behaviour.** `IndexerService.handleEvent`, the
   transaction, the `processed_events` claim and the four DLQ reasons (`invalid-json`,
   `invalid-envelope`, `invalid-payload`, `transient-exhausted`) are byte-for-byte what `srch-001`
   shipped. Rejected: rewriting indexing in a refactor task — a red index test then has two
   possible causes.
2. **One controller, one consumer, one commit protocol.** A second `ServerKafka` per topic would
   be a second group with its own offsets over the same partitions. A new topic is one method
   here plus one entry in `SEARCH_KAFKA_TOPICS`, never a second strategy (D4).
3. **`@Payload()` and `@Ctx()` are load-bearing, not decoration.** A handler that declares no
   parameter decorator is called with the payload only — `RpcContextCreator` falls back to
   `DEFAULT_CALLBACK_METADATA` (one PAYLOAD at index 0) — so the context arrives `undefined` and
   every commit throws on `ctx.getMessage()`. `ctx` is typed `unknown` for two reasons: Nest 12's
   `@EventPattern` overload declares it that way, and `unknown` compiles to `Object` in
   `design:paramtypes`, which is what keeps `ValidationPipe#toValidate` (which skips `String` and
   `Object` and nothing else) from rebuilding the context through `class-transformer`.
4. **`postfixId: ''`, and `autoCommit` under `run`.** Both were read out of the installed
   `@nestjs/microservices@12.3.2` source before a handler was written, not assumed. Without the
   first the service joins `search-svc-server` with a second set of offsets, and `srch-001`'s
   committed positions would be abandoned; without the second the transport acknowledges before
   the side effect. `12.3.2` also imports `getParamArgsMetadata` from `@nestjs/common/internal`,
   so `@nestjs/common` has to be `^12.3.2` — a version skew that fails at import time.
5. **The consumer is started, not awaited, and `KAFKA_CONSUMER_ENABLED` parks it.** Search can
   still answer from PostgreSQL with ingestion down, so a failed start retries every 5 s instead
   of holding the boot. Rejected: fail fast on a missing broker — that turns a Kafka restart into
   a search outage.
6. **The lag gauge starts only after the consumer is up.** A gauge over a group that has not
   joined yet reports the entire topic as lag, which is a false alarm on every cold start.
7. **Delete the old consumer rather than keep it behind a flag.** Two live consumers on the same
   group is the split-partitions defect this task exists to remove, and a flag that can resurrect
   the old loop is a flag somebody will set.

## Verification

| Check | Result |
|---|---|
| `search-svc` `pnpm test` | 120 passed (18 files) |
| `search-svc` `test/search-consumer.controller.spec.ts` | 11 cases: all four topics routed, one strategy, DLQ names from the real publisher, `@Payload`+`@Ctx` wiring, DLQ-failure ⇒ no commit + throw |
| `search-svc` `test/consumer-metrics.spec.ts` | 7 cases: counters delegate, snapshot additive, `lag`/`lastCommit` mapped |
| `search-svc` `pnpm test:e2e` | 92 passed, 1 skipped (8 files; the live spec is gated on `RUN_KAFKA_E2E`) |
| `search-svc` `test/live-kafka.e2e-spec.ts` with `RUN_KAFKA_E2E=1` | 1 passed — "indexes a record consumed by the Nest transport and commits its offset" (3588 ms) |
| `search-svc` `pnpm lint` | 0 warnings, 0 errors (72 files) |
| `search-svc` `npx tsc --noEmit` | exit 0 |
| `search-svc` `nest build` | clean |
| `ecom-infra` `pnpm verify` | 31/31 |
| `kafka-consumer-groups --list` | exactly `cart-svc`, `catalog-svc`, `search-svc`; no `search-svc-server` |
| commit | `search-svc` `84dea4a` (22 paths) |

## Open

- `search-svc-server` must stay absent. Since `kafkajs` does not throw for an unknown group,
  `fetchOffsets` is not proof; the check is `describeGroups` state (`Stable` vs `Dead`), which is
  what the catalog live spec asserts for its own group.
- `search.processed_events` still has no retention sweeper (`srch-003` owns the replay/reset
  conflict: a replayed event id is already claimed, so a rebuild must reset or bypass the table).
- `cms.updated` on the `cms.events` transport topic is not routed here and never reaches the
  controller at all; it is classed `ignored` at handler level. `cms-005` decides the topic.
- The lag sampler is in-process only. It reports to `/search/internal/consumer-stats`; nothing
  scrapes it yet, so an alert still has to read the route or the CLI.
