# srch-003 — preserve dual ingestion, add a DLQ replay tool (done, 2026-11-01)

## What

search-svc ingests from two doors that must never disagree: the **Kafka
consumer** (the primary, live path) and the **internal batch endpoint**
(`POST /search/internal/documents`, for backfill, disaster recovery and hermetic
tests). The rule since `srch-001` was "Kafka is the primary path and the internal
batch endpoint is for backfill/tests; share validation and idempotency" — backfill
must not depend on being able to replay Kafka. `srch-003` keeps that dual door
intact and closes the last gap: when the primary path cannot index a record it
parks a dead letter in `<topic>.dlq`, and until now the only way to recover one
was to read it out of the broker by hand and re-publish it somewhere — the exact
"manual copy/paste from the DLQ" that `srch-003`'s stored rationale rejected.

`srch-003` adds a **documented, tested replay tool** that reads a dead-letter
topic and re-publishes each recoverable record back to the topic it came from, so
the normal consumer path runs it again under whatever was fixed in the meantime.
The batch endpoint's contract (`x-service-key`, 500 documents, 1 MB) and the
shared `upsert` / `processed_events` logic are verified to still hold; no
behavior on either ingestion door changed.

## How

- `search-svc/src/events/dlq-replay.ts` (new, pure) — the interpretation of one
  dead-letter record and the decision of what to send, with no broker and no
  database:
  - `planReplay(message)` reads the `KafkaDlqPublisher` record shape
    (`source.topic`, `originalPayload` / `rawValue`, `key`) and returns either a
    `replay` plan (source topic + recovered bytes + carried partition key) or a
    `skip` with a reason. Recovery order: `originalPayload` verbatim, else
    `rawValue`. It skips — never guesses — an absent/non-JSON value, a non-object
    record, a missing `source.topic`, a source topic that is itself a `.dlq` (a
    replay loop), and a record carrying no recoverable body.
  - `replayMessages(messages, producer, logger?)` runs a pass over a batch through
    a structural producer port, tallies `replayed` / `skipped` / per-reason counts,
    and **propagates a producer rejection** rather than reporting a silently-short
    replay. A summary fold helper accumulates the per-topic tallies.
- `search-svc/src/events/dlq-replay.cli.ts` (new, thin wiring) — a one-shot tool
  (`node --env-file=.env dist/events/dlq-replay.cli.js`, wired as
  `pnpm replay:dlq`). For each requested source topic it drains `<topic>.dlq` from
  the beginning under a short-lived `search-svc-dlq-replay-*` group (so the live
  `search-svc` group's committed offsets are untouched), feeds every message
  through `replayMessages`, and exits on an idle window or a `--max` safety cap.
  It is guarded so importing it never opens a socket. The whole tool is the broker
  adapter around the pure core — all of its logic is unit-tested there.
- `search-svc/README.md` — a "DLQ replay" section under Event Consumption: the
  dead-letter record shape, the invocation, and why re-running is safe.
- Tests: `search-svc/test/dlq-replay.spec.ts` (new, 16 unit cases) covers the
  recovered envelope, the `rawValue` fallback and precedence, Buffer/string/key
  decoding, null keys, every skip branch, a fake-producer pass with mixed
  replay/skip ordering and tallies, the propagated producer rejection, the
  per-skip warning, and the summary merge.

## Decisions (+ one rejected alternative each)

1. **Re-publish to the *source topic*, not straight into the index.** The replay
   goes back through the normal consumer path, so validation, interpretation and
   the `processed_events` claim happen exactly as they would for a live event.
   Rejected: decode the dead letter and call `IndexerService.upsert` directly — it
   would make the replay path a fourth copy of ingestion logic that can drift from
   the two it is supposed to agree with.
2. **A pure core + a thin CLI, not one kafkajs-bound blob.** `planReplay` /
   `replayMessages` are dependency-free and take a structural producer, so the
   meaning of a dead-letter record is unit-tested without a broker; only the
   connection wiring sits in the CLI. Rejected: a single script that talks to a
   broker — it is untestable at the default (broker-less) `pnpm test:e2e`, which is
   the level everything else in this repo is gated at.
3. **Replay the recovered body verbatim; the operator fixes the real cause.** The
   tool never edits a payload. A `transient-exhausted` record (DB was down) is
   simply re-run; a `invalid-payload` record is re-emitted unchanged and only
   lands once the producer's contract is corrected. Rejected: let the tool mutate
   or "repair" payloads — silent rewriting of the source of truth is worse than a
   second dead letter.
4. **A dead-lettered event was never claimed, so the `srch-002` replay/reset
   conflict does not need a sweeper here.** Because `markProcessed` and the
   `upsert` share one transaction, a record that reached the DLQ rolled back and
   left no `processed_events` row — a replay claims it fresh. In the one edge case
   where the id *is* already claimed (a corrected duplicate landed first), the
   consumer reports it `duplicate` and commits: a harmless no-op. Rejected: clear
   `processed_events` rows as part of replay — deleting dedupe state to force a
   re-write would re-open double-application on genuinely-new deliveries.
5. **A short-lived `-replay` group instead of committing on the live group.**
   Reading `<topic>.dlq` under its own group from the beginning never disturbs the
   `search-svc` group's offsets. Rejected: subscribe the replay to the live group —
   it would advance offsets the index path depends on.

## Acceptance (verified)

| Criterion | Where it holds |
|---|---|
| Batch endpoint still requires `x-service-key` and enforces 500 docs / 1 MB | `ServiceKeyGuard` (401), `ingestSearchDocumentsSchema` `.min(1).max(500)` (400 `VALIDATION_FAILED`), `configureApp` json limit `1mb` (413 `PAYLOAD_TOO_LARGE`). Tested in `security.e2e-spec.ts` + `indexer.e2e-spec.ts`. |
| Batch and Kafka use the same `upsert` and `processed_events` logic | Both go through `IndexerRepository.upsert`; the Kafka path additionally claims `markProcessed` in one transaction (`IndexerService.handleEvent`). Tested via the idempotent-replay / stale-rejection / duplicate cases in `indexer.e2e-spec.ts`. |
| DLQ replay is documented and tested | `README.md` "DLQ replay" + `src/events/dlq-replay.ts`/`.cli.ts`; `test/dlq-replay.spec.ts` (16 unit cases). |
| Contracts pin as appropriate | Kept the pinned `@ecom/contracts` **1.9.0** (vendored) and `@ecom/messaging` 0.3.0 — the code compiles and all suites run against them. The acceptance's "1.3.0/2.0.0" is stale numbering; 2.0.0 is a separate release-train task (`ec-004`), not a search-svc concern. |

## Verification

| Check | Result |
|---|---|
| `search-svc` `pnpm typecheck` (`tsc --noEmit`) | exit 0 (src + test) |
| `search-svc` `pnpm test` | 136 passed (19 files); `dlq-replay.spec.ts` = 16 of them |
| `search-svc` `pnpm test:e2e` | 92 passed, 1 skipped (`live-kafka` gated); batch-limit + service-key assertions green |
| `search-svc` `pnpm lint` | 0 warnings, 0 errors (75 files) |
| `search-svc` `pnpm build` | clean; `dist/events/dlq-replay.js` + `dist/events/dlq-replay.cli.js` emitted (matches `replay:dlq` script path) |
| e2e note | `ecom_search_test` had 2 stale non-seed `search_documents` rows (`Contract Guard Item`, `Brand New Product`) from an unrelated older run that broke the seed-verification assertion; removed them to restore the 12-row seed the schema spec expects. No repo code writes those rows. |
| commit | `search-svc` (5 files: 2 new src, 1 new test, README, package.json), local-only |
