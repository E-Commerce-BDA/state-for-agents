# cms-005 — cms-svc: Mongo transaction + cms_outbox for cms.updated and blog.updated (done, 2026-10-31)

## What

cms-svc published `cms.updated` straight from the request handler, on the transport topic
`cms.events`, after `save()` returned and with no record of the attempt. A failed publish left
edited content that no consumer ever heard about, and the topic name was wrong for every
consumer in the registry. This task puts every content mutation in one Mongo transaction —
document write, revision bump, `cms_outbox` insert — and lets the shared `@ecom/messaging`
0.2.0 relay publish `cms.updated` / `blog.updated`. Cache invalidation moved to after the
commit, because Redis cannot join a Mongo transaction.

## How

- `src/db/mongo-tx.ts` — `withMongoTransaction<T>(connection, fn: (session: ClientSession) =>
  Promise<T>)` built on `connection.startSession()` + `session.withTransaction(fn)`, with a
  comment that `directConnection=true` on the replica-set member is what makes this legal
  (already true in `test/setup-env.ts` and the local `MONGODB_URI`). The callback must be
  re-runnable, because `withTransaction` retries on a transient error.
- `src/outbox/cms-outbox.ts` (+ `cms-outbox.module.ts`) — `CmsOutbox.record(session, write)`
  where `write` is `CmsUpdatedWrite | BlogUpdatedWrite`. It injects
  `OutboxStorePort<MongoSessionLike>`, defaults `aggregateType` to `cms`/`blog` and lets a
  caller narrow it (pages pass `page`, sections pass `section`), and calls
  `OUTBOX_STORE.write(session, ...)` so the payload is validated by the contracts schema
  inside the transaction.
- `src/app.module.ts` — `createMongoOutboxModule({ collection: 'cms_outbox', producer:
  'cms-svc', clientId: 'cms-svc', db: () => connection.db })`, injecting the Mongoose
  `Connection` rather than reaching for mongoose internals. `cms_outbox` needs no migration:
  `OutboxInitializer` creates the unique `event_id` index and the partial pending index at
  boot, even when the relay is disabled.
- **13 mutation sites** converted to one shape — write, bump, insert, then invalidate cache:
  `pages.service.ts` (3), `sections.service.ts` (4), `blogs.service.ts` (3),
  `navigation.service.ts` (1), `settings.service.ts` (2). `revisionService.bumpVersion({
  session })` gained the optional `{ session }` so the revision increments inside the same
  transaction — otherwise the payload's `version` could describe a version that never
  committed.
- `src/events/events.service.ts` — loses `publishCmsUpdated` / `publishBlogUpdated`; keeps
  `publishResizeImageJob` (`media.tasks` stays on the direct bus per D10 of the plan, until
  `cms-006` moves it to SQS).
- Deps: `@ecom/contracts` 1.7.0 → 1.8.0, `@ecom/messaging` 0.2.0 added.
- Tests: `vitest.config.e2e.ts` gained `env: { DISABLE_OUTBOX_RELAY: 'true' }` (the relay flag
  is read while the module is declared, so it must be in the environment before boot);
  `test/outbox.e2e-spec.ts` (6 cases) and `test/live-kafka.e2e-spec.ts`; the 13 unit specs got
  a `fakeSession`, a `run` stub and a `CmsOutbox` double.

## Decisions

1. **`cms.updated` is the topic, `cms.events` is gone.** The relay keys on `event_type`, and
   `EVENT_TOPICS` names the topic `cms.updated`, so a row parked under the old transport alias
   would be an unknown topic to every consumer. Rejected: teach the relay about transport
   aliases (D9).
2. **One transaction, then the cache.** Redis cannot join a Mongo transaction, and
   invalidating first lets a reader re-cache the pre-commit state. Rejected: invalidate inside
   the transaction, which produces a false cache miss window (D8).
3. **`bumpVersion({ session })` instead of bumping after commit.** A document and a revision
   that can disagree is the same defect as a document and an event that can disagree.
   Rejected: bump outside, then stamp the payload with the version it reports.
4. **A second store behind one port, not a cms-local relay.**
   `OutboxStorePort<Ctx = Queryable>` keeps the Postgres call sites source-compatible while
   Mongo passes a session. Rejected: a cms-specific relay, which duplicates claim, lease and
   backoff logic — the thing the package exists to prevent (D1, D2).
5. **`media.tasks` stays on the direct bus.** It is not an `EventTopic` (the registry has 11,
   none of them `media.tasks`), so the relay would park it as unknown; `cms-006` moves it to
   SQS. Rejected: force a fake topic into the registry (D10).
6. **No migration file for `cms_outbox`.** Index creation belongs to `store.initialize()`,
   which runs at boot through `OutboxInitializer`, so there is one definition of the indexes
   for every environment. Rejected: a hand-applied JS migration outside the package.

## Verification

| Check | Result |
|---|---|
| `pnpm lint` | 0 warnings / 0 errors (96 files) |
| `pnpm build` | exit 0 |
| `pnpm test` | 132 passed (20 files) |
| `pnpm test:e2e` (relay disabled) | 81 passed, 2 skipped |
| `test/outbox.e2e-spec.ts` | 6/6 — one valid `cms.updated` doc per page mutation; drain through the real relay with a recording publisher → `published`; three docs for create/update/delete with ascending payload `version`s; section/navigation/settings aggregates with their own payload scopes; `blog.updated` for a published blog; **rollback proof**: a raw `withMongoTransaction` that writes a page, bumps the revision and then fails payload validation leaves no page (404), no outbox doc, and the version unchanged |
| `RUN_KAFKA_E2E=1 pnpm test:e2e -- test/live-kafka.e2e-spec.ts` | 2/2 — `cms.updated` and `blog.updated` consumed from the real broker |
| `kafka-console-consumer` (in `ecom-kafka`) | one record on each topic, `producer: cms-svc`, key = aggregate id, envelope parses |
| driver shape | mongodb ~6.20 resolves `findOneAndUpdate` to the bare document instead of `{ value }`; `unwrapDocument()` in the package handles both, and all five services were reinstalled against the fixed tarball |
| commit | `cms-svc` `c0257d8` |

## Open

- Committed on 2026-10-31 as `c0257d8`. The gate re-run that day was lint (0/0, 96 files), 132
  unit tests in 20 files and `nest build`; e2e was **not** re-run because the compose stack was
  down, so the 81 + 2 skipped above is the 2026-10-31 run.
- `cms_outbox` has no retention sweep and no metrics endpoint; the collection grows for the
  life of the database while the topics keep 7 days.
- `media.tasks` is still produced on Kafka by `publishResizeImageJob`; `cms-006` moves it to
  SQS.
- There is no `cms.updated` Kafka consumer by design (storefront invalidation is the
  `/api/revalidate` webhook), so the end-to-end proof is the broker, not a consumer.
- `session.withTransaction` retries mean every converted callback must stay idempotent; the
  current ones are (they only append and bump), but a future read-modify-write needs care.
