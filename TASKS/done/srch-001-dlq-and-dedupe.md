# srch-001 — DLQ malformed events and persist `processed_events`

- Repo: `search-svc` (+ `Documentation`)
- Phase: P0 · kind: bug · transport: kafka-consumer
- Started: 2026-10-30 · Finished: 2026-10-30

## What the defect was

1. `processMessage` committed and dropped a message whose body was not JSON. Nothing
   reached `<topic>.dlq`, so a producer regression was invisible and unreplayable.
2. `IndexerService.handleEvent` had no notion of event identity, so an at-least-once
   redelivery re-ran the upsert. `search_documents.source_updated_at` is a last-writer
   rule, so the replay was indistinguishable from a stale update and got reported as
   `skipped` — a healthy-looking counter on top of work that should not have happened.
3. There was no counter of any kind, so "how many events did we drop?" had no answer.

## How it was fixed

### Contracts first

Repinned `@ecom/contracts` 1.2.0 → **1.7.0** (the plan said 1.5.0; 1.6.0/1.7.0 only
touched `catalog.ts`/`theme.ts`/`index.ts`, so there is no search fallout) to get
`readEventEnvelope`, `isEventTopic`, `parseEventPayload`, `EVENT_TOPICS` and
`dlqTopicName`. The lockfile needed `pnpm install --lockfile-only --ignore-workspace
--force`: pnpm was reading the root `pnpm-workspace.yaml` (which excludes
`search-svc/**`) and answering "Already up to date" while `node_modules` stayed at
1.2.0. Diff after the flag: 7 lines, contracts only.

### One classifier, before any database work

`src/events/event-interpreter.ts` is a pure function — no Kafka, no Postgres:

1. `readEventEnvelope` normalizes the legacy `topic`/`eventType` dual-write and
   validates the envelope.
2. `isEventTopic` — in the contract registry at all?
3. `isSearchTopic` — one of the four we consume?
4. `parseEventPayload` — does the payload match that topic's schema?
5. `EventMapper.mapToSearchDocument` — can it become a `SearchDocument`?

It returns `mapped` / `ignored` (with a reason) / `invalid` (with a stage and a Zod
summary clipped to 3 issues / 300 chars, because a 40-field path dump in a log line
is not a diagnostic). `SEARCH_KAFKA_TOPICS` moved to `search-topics.ts` so the
interpreter does not import the consumer that imports it.

### Dedupe inside the upsert transaction

`db/003-processed-events.sql` adds `search.processed_events` PK on `event_id`.
`IndexerRepository` gained `withTransaction` (`BEGIN`/`COMMIT`/`ROLLBACK`/`release`),
`markProcessed(client, eventId, topic)` and `upsert(doc, client?)`.
`handleEvent` now claims the id with
`INSERT ... ON CONFLICT (event_id) DO NOTHING RETURNING event_id` and upserts the
document **in the same transaction**: `rowCount = 0` is the `duplicate` outcome, and
a failed upsert rolls the claim back so the retry can still apply it.

### DLQ policy

| Record | Retry | DLQ | Offset |
|---|---|---|---|
| Body is not JSON | none | `invalid-json` + `rawValue` | after the write |
| Envelope fails validation | none | `invalid-envelope` + `originalPayload` | after the write |
| Payload fails the topic schema | none | `invalid-payload` + `originalPayload` | after the write |
| Unknown / unsubscribed / unmappable | n/a | — | commit + `warn` |
| Infrastructure error | 1/2/4/8/16s | `transient-exhausted` | after the write |

The invariant is unchanged and now pinned by a test: `commitOffsets` runs **only**
after `producer.send` resolves, so a failed DLQ write leaves the record for redelivery
instead of losing it. Every DLQ publish is unconditional (no key) — a dead letter must
not be partitioned away from the operator looking for it.

### Visibility

`ConsumerMetrics` (six counters) is injectable but the consumers fall back to a local
instance, so the existing unit tests still construct them directly while Nest injects
the module singleton in the app. Exposed as
`GET /api/v1/search/internal/consumer-stats` behind `ServiceKeyGuard`,
`Cache-Control: no-store`. `invalid` (the verdict) and `dlq` (the delivery) are
counted separately on purpose: a failed publish leaves both at zero, which is exactly
the state the retry ladder needs to own.

## Decisions and the alternatives that were rejected

| Decision | Reason | Rejected alternative |
|---|---|---|
| A `processed_events` table, not a column on `search_documents` | An id already applied to product 7 can still arrive for product 9; and the document row is overwritten by a later event, so it cannot remember the id that wrote it | `last_event_id` on `search_documents` — loses history and cannot answer "did I already apply *this* id" after the next event |
| Claim and upsert in **one** transaction | A crash between the two would leave an id claimed for a document never written — a permanent, silent hole, the worst possible failure for an index | Claim first, then upsert (cheaper, but unrecoverable); or dedupe in Redis (adds a second source of truth to a task about exactly that) |
| `event-interpreter` as a pure function | The classification is the risky part and it is now testable without Kafka or Postgres; the Kafka and in-memory paths cannot drift because they share it | Classification inline in the consumer — untestable, and the in-memory path would need a copy |
| No retries for schema failures | A payload that fails a strict schema will fail it forever; retrying only parks the partition behind a poison record for 31 seconds per attempt | Retry everything — simple, and it stalls all four topics' partitions on one bad producer deploy |
| Counters in-process | "Since the last deploy" is the question an operator asks during an incident, and it needs no new infrastructure | A metrics backend (Prometheus/OTel) — real, but a separate task and a new dependency for a P0 bug fix |
| `processed_events` retention left as a seam, not a sweep | The index is not a source of truth: dropping a very old processed id at worst re-applies an old event, which the stale-timestamp guard already handles | An unbounded table; or a sweep inside this task, which would need a scheduler the service does not have yet |

## Verification

- `pnpm typecheck` exit 0; `pnpm lint` **0 warnings / 0 errors** (69 files);
  `pnpm build` exit 0.
- `pnpm test`: **18 files, 117 tests green** (was 16/98). New: `event-interpreter.spec.ts`
  (7 — every outcome, the deactivation signal, the error trimming),
  `consumer-metrics.spec.ts` (5); `kafka-event-consumer.spec.ts` rewritten (11 —
  malformed JSON → DLQ + commit, invalid payload → no retry, ignored/duplicate →
  commit + counter, the ladder, DLQ-write failure → **no** commit, and that failure
  leaving `invalid`/`dlq` at zero); `indexer.service.spec.ts` rewritten around the
  `HandleEventOutcome` union.
- `pnpm test:e2e` (Postgres 5433): **8 files, 92 tests green**. `indexer.e2e-spec.ts`
  now sends real envelope ids and cleans `processed_events`; the dedupe case
  redelivers the same id with a **newer** timestamp and a different title → reported
  `duplicate` and the row keeps "First Delivery", so the stale guard cannot be the
  cause of the pass. A new invalid-payload case asserts the index is untouched. The
  stats route is covered behind the service key. `schema.e2e-spec.ts` gained a
  `processed_events` describe (columns, PK, retention index, `ON CONFLICT DO
  NOTHING`).
- `db/003` applied to `ecom` and `ecom_search_test`. No Kafka broker was required.
- Docs: `Documentation/services/search.md` (§3.2 drift fixed — strict `>`, null
  popularity preserved; §3.3 dedupe; §4.5 stats; §5 classification/DLQ policy),
  `Documentation/3.Database-Schema.md` (`processed_events` + why it exists),
  `Documentation/4.API-Design.md` (§3.9 row, §4.11d contract, §6 DLQ sentence, §7
  internal-map row), `search-svc/README.md` (`db/003`, stats route, Event
  Consumption).
- Commits, one intent each: `7cdc505` (deps), `cdb508e` (interpreter),
  `e6d46d3` (dedupe), `d4f1e17` (DLQ routing), `170f39b` (stats route),
  `06137cf` (tests), `8457867` (README) in `search-svc`; `055e585`, `aef1626`,
  `8a8fbfb` in `Documentation`. No push, tag, or release.

## Open

- **Log replay and dedupe disagree by design.** Replaying `product.imported` to
  rebuild the index now hits `ON CONFLICT DO NOTHING` for every id that was already
  applied, so a naive replay is a no-op. A rebuild has to reset
  `search.processed_events` (or carry a force flag) — that belongs with the replay
  work in `srch-003`, and the two must not be implemented independently.
- Retention sweep for `processed_events`: `idx_processed_events_processed_at` exists
  for `DELETE ... WHERE processed_at < now() - interval '30 days'`, but nothing runs
  it yet; the service has no scheduler.
- `cms.updated` still arrives on the `cms.events` transport topic and is classified
  `ignored` rather than mapped — correct for this consumer, and it falls out of
  `srch-001` because the fix was never topic plumbing. `cms-005` (outbox +
  `cms.updated`/`blog.updated`) is where that gets decided.
