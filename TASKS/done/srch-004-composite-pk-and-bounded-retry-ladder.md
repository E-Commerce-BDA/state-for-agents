# srch-004 — composite document identity, a session-bounded retry ladder, and a reindex that cannot lie (done, 2026-11-03)

- Repos: `search-svc` + `@ecom/messaging` 0.5.0 (+ `ecom-infra` reindex script, `Documentation`)
- Phase: P0 · priority: P1 · kind: bugfix · transport: kafka-consumer
- Started: 2026-11-03 · Finished: 2026-11-03

## What

Three independent defects, one outage. **None of it was found by a test — it was
found live**, and that is the honest headline of this task: `pnpm test`,
`pnpm test:e2e` and `pnpm lint` were green before, during and after.

1. **Schema.** `search.search_documents` was declared
   `CONSTRAINT search_documents_pkey PRIMARY KEY (id)` while every upsert conflicts
   `ON CONFLICT (document_type, id)`. Postgres lets the arbiter match the PK only if
   the index predicate matches exactly; here `PRIMARY KEY (id)` is a *different*,
   stricter constraint, so a product and a category carrying the same id raised
   `23505 unique_violation` on a write the upsert was supposed to absorb.
2. **Consumer liveness.** `@ecom/messaging`'s retry ladder is 1/2/4/8/16 s = 31 s of
   sleeps, and the consumer set **no session timeout at all**, so kafkajs's 30 s
   default applied. The member was evicted while it was still sleeping, and
   `UNKNOWN_MEMBER_ID` then failed both the DLQ publish and the offset commit. The
   group re-joined and replayed the same offset forever: a permanent wedge with no
   dead letter and no advancing offset.
3. **Dev data.** `002-seed-search.sql` hand-authors category ids
   (`…0101/0102/0103`) that collide with catalog's product *fixture* ids, and
   `search-svc/README.md` told a developer to apply it to the shared `ecom`
   database. Legacy and e2e rows were orphaned in that index.

The outage was defect 1 arriving on defect 2's timing: offset 61 on
`product.updated` partition 2 carried `fixture-tee`, whose id is also a seeded
category id. The upsert threw 23505, the ladder outran the session, the commit
died, and the partition never moved. Search kept answering from PostgreSQL, so
every HTTP surface still looked healthy.

**Why the suites could not have caught it:** the hermetic e2e runs against
`ecom_search_test`, which contains *only* the search seed — no `catalog.products`
rows — so the two ids that collide in the dev database never met. Consumer specs
drive the controller through `InMemoryEventConsumer`, which has no broker, no group
and no session, so nothing in-process could observe a heartbeat timeout. The defect
needed a shared database with two writers, which is exactly what a local stack is.

## How

### Schema — the identity is `(document_type, id)`

- `search-svc/db/004-search-documents-composite-pk.sql` (new, idempotent, one
  transaction) — drops `search_documents_pkey`, drops the now-redundant
  `search_documents_type_id_key` unique index, re-adds
  `PRIMARY KEY (document_type, id)`. The unique index is redundant because the new
  PK index covers exactly those two columns, and `ON CONFLICT (document_type, id)`
  matches a PK constraint the same way it matched the index.
- `search-svc/db/001-search-schema.sql` — fresh installs get the composite PK from
  the start; the `search_documents_type_id_key` block and its comment ("Explicit
  target for ON CONFLICT … upserts") are gone, replaced by a comment naming the PK
  as the arbiter.
- `src/indexer/indexer.repository.ts` — no query change. `upsert` and `forceUpsert`
  now carry a comment stating that the `ON CONFLICT` arbiter *is* the primary key,
  which is the fact a future editor must not break.

### `@ecom/messaging` 0.5.0 — the ladder gets a budget it can prove

- `src/consumer/kafka-consumer.strategy.ts` — `sessionTimeoutMs` /
  `heartbeatIntervalMs` options, exported
  `DEFAULT_SESSION_TIMEOUT_MS = 45_000` and
  `DEFAULT_HEARTBEAT_INTERVAL_MS = 3_000`, passed into `consumer: { … }`. 45 s is
  chosen so a documented ladder fits with margin instead of being silently cut by a
  library default.
- `src/consumer/kafka-event-handler.ts` — new `retryBudgetMs` option. When set, the
  ladder is truncated **at construction** so the sum of sleeps stays inside the
  budget (always keeping at least one sleep) and `maxRetries` follows the truncated
  length; the strategy logs
  `Retry ladder bounded to 20000ms of sleeps: 5 configured delays reduced to 1000/2000/4000/8000 (4 retries).`
  When omitted, behaviour is byte-for-byte what 0.4.0 did. `KafkaConsumerStalledError`
  semantics are untouched.
- Entry-point split found while wiring the above: `src/index.ts` no longer re-exports
  the SQS task surface (which pulls `@aws-sdk/client-sqs` into every consumer-only
  install); `src/nest/consumer.ts` is the new subpath for the consumer Nest helpers,
  and `test/entry-points.spec.ts` guards the boundary. `src/tasks/index.ts` — the
  barrel the `./tasks` export has pointed at since 0.4.0 — was never committed; it is
  part of this commit.
- `package.json` 0.4.0 → **0.5.0**, `CHANGELOG.md` 0.5.0 entry ("the ladder was sized
  against nothing"), `README.md` outcome table gains the budget row;
  `ecom-messaging-0.5.0.tgz` packed and committed like 0.3.0/0.4.0.
- Two artifacts the **0.4.0 commit had left untracked** are in this commit: `src/tasks/index.ts`
  (the barrel the `./tasks` export has pointed at since 0.4.0 — without it a fresh clone of
  the package does not build) and `ecom-messaging-0.4.0.tgz` (which cms-svc's `file:` pin
  names). Both are *additions*, not deletions; no `dist/` or tarball was removed.

### `search-svc` — park the unrecoverable on the first attempt

- `package.json` repinned to `file:../ecom-messaging/ecom-messaging-0.5.0.tgz`. Only
  search-svc moves; cart-svc and catalog-svc stay on 0.3.0 by decision.
- `src/events/index-errors.ts` (new) — `translateIndexError()` returns
  `index-constraint-violation` for SQLSTATE `23505` and `null` otherwise, so a
  deterministic constraint breach is terminal exactly like `invalid-payload`, while a
  deadlock or a refused connection stays retryable.
- `src/events/events.module.ts` — `translateError: translateIndexError` and
  `retryBudgetMs: RETRY_BUDGET_MS` (`20_000`) on the `KafkaEventHandler` factory: 20 s
  against a 45 s session, five handler attempts, matching the `maxReceiveCount 5`
  parity the SQS relay already claims. No new env var — the timeout is a reviewed code
  constant, like the per-service timeouts in the storefront's `lib/services/urls.ts`.
- `src/app.setup.ts` + `src/events/search-consumer.controller.ts` import from
  `@ecom/messaging/nest/consumer`.

### Tests — the cases that would have caught this

- `test/schema.e2e-spec.ts` — asserts `pg_get_constraintdef` is
  `PRIMARY KEY (document_type, id)`, asserts `search_documents_type_id_key` is gone,
  and the regression case: the same id inserted under `product` and under `category`
  coexists, then an `ON CONFLICT (document_type, id)` upsert of the colliding id
  writes instead of raising.
- `test/indexer.e2e-spec.ts` — `IndexerRepository.upsert` accepts a cross-type same
  id, and `pruneMissing('category', ids)` leaves the same-id `product` row alive.
- `src/events/index-errors.spec.ts` (new) — 23505 → terminal; `40001` and
  `ECONNREFUSED` → `null`.
- `test/search-consumer.controller.spec.ts` — a repository throwing 23505
  dead-letters on the **first** attempt with reason `index-constraint-violation` and
  the offset still commits: no ladder walked.
- `ecom-messaging` `test/consumer/kafka-consumer.strategy.spec.ts` — emitted config
  carries `sessionTimeout: 45000` / `heartbeatInterval: 3000`, and an explicit
  override wins. `test/consumer/kafka-event-handler.spec.ts` — with
  `retryBudgetMs: 20_000` the slept total is ≤ 20000, the attempt count follows the
  truncated ladder, and the record still dead-letters and commits; without the option
  the ladder is exactly 1/2/4/8/16 s.

### Dev data — rebuilt from truth, one page per type

- `ecom-infra/scripts/search/reindex.mjs` rewritten. `collectCompleteList()` fetches
  one page and **throws if the response carries `nextCursor`**; `reconcile()` drops a
  failing type from the payload entirely instead of half-loading it; `mapType()`
  dedupes by id and reports skipped/collapsed counts; the result carries
  `unreconciled`. Categories are read with `includeInactive=true`, and
  `toCategoryDocument` now maps status from `isActive` — the old mapper read a
  `status` field that category rows do not have, so every reindexed category was
  written `inactive` and invisible to every query.
- Why the payload must be complete: `IndexerService.reindex()` upserts the batch,
  groups ids by type, and calls `pruneMissing(type, ids)` **per type present**. A
  partial read of a type is a destructive delete of that type's live documents.
- `search-svc/README.md` — the two database blocks are separated: **development**
  applies `001`, `003`, `004` and is populated by events plus `pnpm search:reindex`;
  **e2e test** applies `001`, `002`, `003`, `004`. Failure table gains the
  constraint-violation row.
- `002-seed-search.sql` was **not** edited and the seed-count assertions in
  `test/schema.e2e-spec.ts` were **not** touched: the seed is the test suite's
  fixture and stays test-DB-only.

## Decisions (+ one rejected alternative each)

1. **Identity is the composite primary key.** Migration 004 makes
   `(document_type, id)` the PK so it *is* the arbiter the upsert already named.
   Rejected: re-point the query at `ON CONFLICT (id)`, which would let a category
   document silently overwrite a product one — the collision would stop erroring and
   start corrupting.
2. **The session timeout is set explicitly by the strategy, not inherited.**
   Rejected: raise only the timeout (45 s covers today's ladder and still lets the
   next handler that adds a delay re-open the same outage).
3. **The retry budget truncates the ladder at construction.** `maxRetries` and the
   ladder length stay consistent and one warning line tells the operator what the
   service will actually do. Rejected: cap the sleep per message at retry time,
   which leaves a reported `maxRetries` the code will never reach.
4. **A 23505 from the index write is terminal on attempt 1.** Rejected: walk the
   ladder over it — redelivery cannot repair a deterministic constraint breach, and
   walking one is precisely what wedged the partition.
5. **The reindex refuses an incomplete read rather than trusting a cursor.**
   Rejected: walk `/api/v1/products`' cursor, measured to repeat 78 of page 1's 100
   rows; and rejected: fix catalog-svc inside this wave, because that is another
   repo's contract and would have dragged an unrelated release train into a P0.
6. **Dev stops applying the search seed; the seed stays test-only.** Rejected: edit
   `002-seed-search.sql` — its ids are load-bearing for the e2e suite's assertions,
   and the seed is only wrong when it is pointed at a database that also holds
   catalog data.

## Acceptance (verified)

| Criterion | Where it holds |
|---|---|
| Composite PK in the migration, the fresh-install DDL and both live databases | `db/004-…sql` applied to `ecom` and `ecom_search_test`; `pg_get_constraintdef` asserted in `test/schema.e2e-spec.ts`. |
| A product and a category may share an id; the upsert writes, the prune spares | `test/schema.e2e-spec.ts` regression case + `test/indexer.e2e-spec.ts` cross-type upsert and `pruneMissing` cases. |
| Consumer config carries 45 s / 3 s and an override wins | `kafka-consumer.strategy.spec.ts`. |
| The slept total respects `retryBudgetMs`, and is unchanged without it | `kafka-event-handler.spec.ts` (truncated ladder + full 1/2/4/8/16 s ladder). |
| 23505 dead-letters on attempt 1 and commits | `index-errors.spec.ts` + `search-consumer.controller.spec.ts`. |
| Index rebuilt from sources, no orphans | Live `internal/stats` + orphan SQL with the `deleted_at IS NULL` floor. |
| Docs state the composite identity and the bounded ladder | `3.Database-Schema.md` §search_documents, `services/search.md` §2.3/§3.1/§3.4, `1.Architecture.md` §6.4, `9.Testing.md` DLQ row, `8.Versioning.md`, `search-svc/README.md`. |

## Verification

| Check | Result |
|---|---|
| `ecom-infra` `pnpm verify` | 31 passed, all containers healthy |
| `ecom-messaging` `pnpm build` / `pnpm test` / `pnpm pack` | clean; **136 passed in 13 files**; `ecom-messaging-0.5.0.tgz` produced |
| `search-svc` `pnpm install` / `lint` / `build` | install green on the 0.5.0 tarball; lint 0 warnings 0 errors; build clean |
| `search-svc` `pnpm test` | **142 passed in 20 files** (was 120/18) |
| `search-svc` `pnpm test:e2e` | **96 passed, 1 skipped** across 9 files (was 92); includes the cross-type PK and prune cases |
| Live boot, catalog + cms + search | Boot log shows the ladder-truncation warning and `Consumer has joined the group` on all four topics; `Exhausted retries` and `UNKNOWN_MEMBER_ID` never appear |
| The wedge cleared | `product.updated` partition 2 advanced past the old offset 61 (154 → 158); no group or offset surgery was needed — offset 61 became a legal upsert under the composite PK |
| `GET /search/internal/stats` | `{"documents":28,"active":28,"byType":{"product":16,"category":9,"blog":3}}` |
| Category count vs source | 9 indexed = 9 `catalog.categories` rows with `deleted_at IS NULL`. The plan's "40" counted **physical** rows; 31 are soft-deleted "Accessories E2E" rows the source API filters out. |
| Orphans | 0 products, 0 categories, 0 blogs (`NOT EXISTS` against the owning table with the delete floor); `cart-tee%` rows 0 |
| `reindex.mjs`, first run | `HTTP 400 … limit must not be greater than 100` → products never fetched, **12 indexed / 6 pruned**, and the script still reported success. This is the plan's named contingency, and why the script was rewritten. |
| `reindex.mjs`, second run (cursor walk) | `212 products / 27 pruned` reported, but only 127 distinct product docs landed and 140 non-draft catalog products were missing — the cursor's 78/100 page overlap. Rejected as unusable; catalog-svc's defect recorded as a follow-up. |
| `reindex.mjs`, final run | **16 products (16 mapped) / 9 categories (9 mapped) / 3 blogs (3 mapped) → 28 indexed, 113 pruned**, all types `active` |
| `product.updated.dlq` | 8 records (3 + 5 across partitions), not "many": two distinct event ids from the wedge. `pnpm replay:dlq` → **Replayed 8, skipped 0**; the live consumer logged all eight as already applied, and `internal/consumer-stats` moved to `duplicate: 8, commit: 8, dlq: 0, stalled: 0` with lag 0 on every topic — the predicted harmless repeat, proven rather than assumed. |
| `GET /search/suggest?q=linen` | "Everyday Linen Shirt" (+ the Apparel category + the linen blog) |
| `GET /search/suggest?q=tee` | "Fixture Tee" and "Heavyweight Pocket Tee"; **"Cart Hydration Tee" gone** |
| Storefront BFF | `GET :3000/api/search/suggest?q=linen` → 200 through `lib/services/urls.ts` → search-svc, same documents |
| Tracker invariants, re-checked by hand | **145 unique ids = 116 done + 0 in-progress + 29 backlog**, 0 duplicates, `id == filename` for every `done` entry, every `done` log resolves on disk, no `todo` carries a log, `summary.byRepo` mirrors the per-repo entries — 0 problems reported |
| commits (all local-only, author `Dharmil Gajjar <foreafcbeta@gmail.com>`) | `ecom-messaging` **`c09a487`** (14 paths: 0.5.0 surface + tests + CHANGELOG/README + both tarballs + `src/tasks/index.ts`), `search-svc` **`f945e83`** (14 paths), `ecom-infra` **`1588688`** (`scripts/search/reindex.mjs` + the `search:reindex` script), `Documentation` **`143efef`** (5 files), `state-for-agents` carries this record and cannot name its own hash |

## Open

- **`CursorPayload.id` is now ambiguous.** The keyset tiebreaker
  (`src/search/cursor.codec.ts`, `src/search/search.repository.ts`) is the bare `id`
  while ids are no longer globally unique. Harmless for the uuid-keyed sources in
  use; a correct fix adds `documentType` to the cursor payload — a wire-format
  change, so it is a task, not a note.
- **`id` is `varchar(64)` but the docs and row types still say uuid.** Changing the
  column type touches `event-mapper.ts`, `db/rows.ts` and the cursor codec.
- **cart-svc and catalog-svc are still on 0.3.0**, so their ladders stay unbounded
  until their next wave; ADR 44 is the constraint they must meet. Seen live while
  verifying this one: catalog-svc loops `order.created` offsets 3 and 4
  ("Reservation … not found") forever, and `order.created.dlq` held **2696**
  records. Out of scope for search, and the clearest possible argument for the ADR.
- **catalog-svc's product cursor is not a walk** — `ORDER BY created_at DESC, id DESC`
  continued by `p.id > cursor` repeats 78 of page 1's 100 rows — so an archived or
  draft product snapshot over HTTP is impossible today. `reindex.mjs` therefore
  indexes active products only, deliberately.
- **e2e suites write into the shared dev index** (`cart-tee-*`); a test-owned purge
  marker is needed so a reindex is not the only cleanup path.
- **Only 16 of 267 non-deleted catalog products are searchable** (246 archived) —
  seed hygiene, not a search defect.
- **cms-svc has no HTTP route that enumerates draft blogs** (public list is
  published-only, admin list is JWT + Roles guarded), so a blog snapshot can only
  ever cover published documents.
- `Documentation/services/search.md` §1 still lists catalog-svc on `:4010`; the real
  port is 4020 (`:4010` is auth-svc). Untouched here to keep the wave's diff to the
  claims it actually verified.
