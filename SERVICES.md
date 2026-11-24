# SERVICES — status matrix (agents update cells as work lands)

> Scope: live tracker. Stages: spec → build → test → verify (⬜ todo / 🚧 in-progress / ✅ done).
> Status: Active | Date: 2026-11-01 | Machine mirror: `tasks.json`

| Repo | Port | Spec doc | spec | build | test | verify |
|---|---|---|---|---|---|---|
| storefront-ui | 3000 | `Documentation/design-system/storefront.md`, `pages/` | ✅ | ✅ | ✅ | ✅ |
| admin-app | 3001 | `Documentation/6.Admin-Panel.md` | 🚧 | ⬜ | ⬜ | ⬜ |
| ecom-contracts | npm | `8.Versioning.md` | ✅ | ✅ | ✅ | ⬜ |
| ecom-messaging | npm | `8.Versioning.md` §10, `1.Architecture.md` §6.5 | ✅ | ✅ | ✅ | ✅ |
| auth-svc | 4010 | `Documentation/services/auth.md` | ✅ | ✅ | ✅ | ✅ |
| catalog-svc | 4020 | `Documentation/services/catalog.md` | 🚧 | ✅ | ✅ | ✅ |
| cart-svc | 4030 | `Documentation/services/cart.md` | ✅ | ✅ | ✅ | ✅ |
| order-svc | 4040 | `Documentation/services/order.md` | ✅ | ✅ | ✅ | ✅ |
| cms-svc | 4050 | `Documentation/services/cms.md` | 🚧 | ✅ | ✅ | ✅ |
| analytics-svc | 4060 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| import-svc | 4070 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| notify-svc | 4080 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| search-svc | 4090 | `Documentation/services/search.md` | ✅ | ✅ | ✅ | ✅ |
| ecom-infra | — | `7.Deployment.md` (to create) | ⬜ | ⬜ | ⬜ | ⬜ |

Rule: flip a cell + update `tasks.json` + `STATUS.md` in the same commit. Link PR/commit in row note.

## Row notes

- `ecom-contracts` — **1.10.0** `08e930c` (`moneySchema` narrowed to `z.number().nonnegative()` — `refundAmount` is one wire type now that order-svc normalises `DECIMAL` at its DB boundary; tarball + CHANGELOG committed, the refund specs flipped to number-only) on top of **1.9.0** `8b4020a` (`productVariantRefSchema` + `productImportedPayloadSchema.variants[]`, the field `cat-008` needed). 3/5 tasks, 117 tests in 5 files at 1.9.0 and green again at 1.10.0, typecheck, build and `pnpm pack` green. `spec`/`build`/`test` are ✅ because the shipped surface is real; `verify` stays ⬜ until `ec-004` (2.0.0) and `ec-005` (release train + storefront repin).
- `storefront-ui` — `sf-051` `268b5d9..6a02b34` on `staging` (19 commits: service registry + `ServiceResult` transports + `bff()`; catalog/cart/order clients; `sf_cid` guest identity with server-side merge; cart/checkout/orders/account BFF handlers; pure-reducer cart store; the nine commerce blocks; all five routes plus home), plus `sf-049` `71f04a5` and `sf-050` `5de7d95`. 51/61 tasks, **116 test files / 904 tests**, `tsc` clean, `next build` clean, live integration gate recorded in the sf-051 log. `build`/`test`/`verify` flipped ✅ for the shipped commerce surface; the open `sf-052` (track beacon, blocked on `anl-002`), `sf-053` (contracts repin) and the `sf-054..sf-061` depth wave add surface, they do not contradict what ships.
- `cart-svc` — `ca-009` `f707431` (consumes `order.created` on the shared Nest transport, converts in the same transaction as its `processed_events` claim, **deletes** the `ca-007` HTTP bridge). **10/10 tasks, queue empty**; **119 unit (17 files) + 96 e2e (2 skipped, 12 files)**, lint 0 (81 files). `verify` flipped to ✅ this pass because the repo-stage condition it was waiting on (`ca-009`) is what closed it. Carried debt, not a task: order-svc's `CartClient` still posts to the deleted route and logs a `404` per checkout until `ord-012`, and there is no `/consumer-stats` route, so the `cart-svc` group is observable only from `kafka-consumer-groups`.
- `catalog-svc` — `cat-008` `9cd6948` (`product.imported` upsert + the `onHand = max(0, imported − openReserved)` stock rule + four DLQ reasons + no outbox re-emit; `KafkaOrderConsumer` replaced by two `@EventPattern` routes on one strategy with `OrderCreatedHandler` untouched). 9/11 tasks, **137 unit (22 files) + 112 e2e (12 files)**, lint 0 (128 files), 3 live cases. `spec` stays 🚧 behind `cat-010` (`order.status.updated` → stock release) and `cat-011` (fixture-seed guard).
- `search-svc` — `srch-002` `84dea4a` (four `@EventPattern` routes, group exactly `search-svc`, `KafkaEventConsumer` and its spec deleted, `KAFKA_CONSUMER_ENABLED` guard, lag/commit on `GET /search/internal/consumer-stats`). 2/3 tasks, **120 unit (18 files) + 92 e2e (1 skipped)**, lint 0 (72 files), 1 live case. `srch-003` (dual ingestion + DLQ replay) is the one open task and it opens no new surface, so the four cells stay ✅.
- `Documentation` — `1.Architecture.md` §6.5, `3.Database-Schema.md`, `4.API-Design.md`, `8.Versioning.md` (1.9.0 row + strict-schema ordering + §10 pin mismatch), `9.Testing.md`, `10.Observability.md`, `services/{cart,catalog,search}.md` all moved this pass; `doc-004` is the one open entry.
- `ecom-messaging` — no task entries of its own; delivered through `au-004`/`ca-008`, re-opened by `cat-007`/`ord-011`/`cms-005`, and extended by `srch-002`/`ca-009`/`cat-008`. Now **0.5.0**: the producer half (Postgres + Mongo stores, all five producers) plus the consumer half (`createKafkaConsumerStrategy`, `KafkaEventHandler`, `ProcessedEventsStore`, `KafkaDlqPublisher`, `KafkaLagSampler`, nine counters), **100 tests in 9 files**.

Cell truth for the rows above was recomputed against `tasks.json#repos[repo].stages` on 2026-11-01. Where a ✅ column and an `in-progress` stage disagree it is because the column records the shipped slices and the stage records the repo — the note says which is which; do not "fix" one without the other. `cart-svc` is the one row where both now say done.
