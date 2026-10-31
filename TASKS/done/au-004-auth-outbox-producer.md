# au-004 — auth-svc: user.registered through a transactional outbox (done, 2026-10-30)

## What

`auth-svc` declared `user.registered` in its messaging block and in three documents, but
nothing produced it: registration was a clean transaction that ended at `COMMIT` and no
Kafka client existed in the repo. This task makes the event real, in the same transaction
as the user row, and gives it a relay that cannot lose it.

## How

- **New shared package `@ecom/messaging` 0.1.0** (built together with ca-008):
  - `src/envelope.ts` — `buildEventEnvelope` writes `type` = `topic` = `eventType`, `version` 1,
    `idempotencyKey` = `id`, then validates with `eventEnvelopeSchema.parse` **and**
    `parseEventPayload(topic, payload)` before returning.
  - `src/outbox/postgres-outbox.store.ts` — `write()` (uses the caller's client, never opens a
    transaction), `claimBatch()` (one `WITH claimed AS (SELECT … FOR UPDATE SKIP LOCKED) UPDATE …`
    statement ordered by `created_at, id`), `markPublished()`, `markFailed()` (attempts+1,
    `failed` at 5, `locked_until` = `now() + min(2^attempts, 60)s`), `tryAcquireRelayLock()`
    (`pg_try_advisory_lock(hashtextextended('<schema>.<table>',0))` on a checked-out client).
  - `src/outbox/outbox.relay.ts` — `drainOnce()` (lock → claim → sequential publish →
    mark → release) and `start()`/`stop()` with an `isProcessing` guard.
  - `src/publishers/kafka.publisher.ts` — `producer({ idempotent: true, maxInFlightRequests: 1 })`,
    `acks: -1`, and it **rethrows**: a relay that swallows a failure marks a lost message published.
  - `src/publishers/{recording,discard}.publisher.ts` — test double and relay-disabled sink.
  - `src/nest/outbox.module.ts` — `createOutboxModule({ schema, producer, clientId, pool, brokers, enabled })`
    provides `OUTBOX_STORE`, `OUTBOX_PUBLISHER`, `OUTBOX_RELAY` and a lifecycle provider that is
    only registered when the relay is enabled.
- `auth-svc/db/003-auth-outbox.sql` — `auth.outbox` with the three CHECKs
  (`aggregate_type IN ('user')`, `event_type = 'user.registered'`, `envelope->>'type' = event_type`,
  `envelope->>'id' = event_id::text`) and `idx_outbox_pending (created_at) WHERE status = 'pending'`.
- `auth-svc/src/outbox/auth-outbox.ts` — `recordUserRegistered(client, user)`; `displayName` is
  `first_name + ' ' + last_name` trimmed and sliced to the schema's 120 chars (the columns allow 201).
- `auth.service.ts` — the call sits **between** `assignUserRole` and `COMMIT`, so a rollback takes
  the event with it. `createOutboxModule(...)` in `AuthModule.imports`; `KAFKA_BROKERS` and
  `DISABLE_OUTBOX_RELAY` in the Joi schema.
- `vitest.config.e2e.ts` — `env: { DISABLE_OUTBOX_RELAY: 'true' }`; without it every e2e run starts
  a real relay against a real broker.

## Decisions

1. **One shared package, not a per-service copy.** The claim SQL, the lease, and the retry ladder
   are the parts that get a bug; three copies means three fixes. Rejected: copy order-svc's
   `outbox/` into auth and cart — ord-011 would make it a third.
2. **Framework-free core, Nest in `./nest`.** `src/index.ts` exports pure TS so the 21 package
   tests need no DI container; the services add one import plus one factory call.
   Rejected: `@nestjs/common` in the main entry, which would drag the container into every unit test.
3. **Store the finished envelope, not the payload.** The relay publishes exactly the bytes that
   were committed and never re-derives anything. Rejected: store the payload and build the
   envelope at publish time — the contract check would then fire after the business commit.
4. **Validate inside the write transaction (fail closed).** `write()` parses before the `INSERT`,
   so contract drift aborts the registration. Accepted cost: a future contract tightening blocks
   writes until it is fixed — visible, unlike a row that can never be published.
5. **Per-schema outbox (`auth.outbox`), not one shared table.** Each service owns its rows and its
   lease budget. Rejected: `messaging.outbox` with a producer column, which couples deployments.
6. **`SKIP LOCKED` + a session advisory lock.** `SKIP LOCKED` stops two workers taking one row; the
   advisory lock keeps a single publisher so per-`userId` order survives a multi-replica
   deployment. Accepted cost: relay throughput is one batch in flight.
7. **Parity with the queue side.** Five attempts and then `failed`, matching `maxReceiveCount = 5`;
   `last_error` is truncated to 500 chars for triage.
8. **`userId` and a display name, never the email.** PII minimization; notify resolves the address
   through au-005 over HTTP. Rejected: embed the email, which spreads PII across topics and logs.
9. **Pre-1.0 (`0.1.0`).** The package will change shape when ord-011 becomes the third adopter;
   `1.0.0` is cut then, per `8.Versioning.md`. Distribution copies the contracts pattern:
   committed tarball + `file:` pin + `pnpm install --ignore-workspace`.

## Verification

| Check | Result |
|---|---|
| `ecom-messaging` `pnpm test` | 21 passed (3 files: envelope 6, store 7, relay 8) |
| `ecom-messaging` `pnpm typecheck` / `build` / `pack` | exit 0 / exit 0 / `ecom-messaging-0.1.0.tgz`, `dist/nest/index.js` present, no `src/` |
| `auth-svc` `pnpm test` | 29 passed (10 files) |
| `auth-svc` `pnpm test:e2e` | 45 passed, 1 skipped (12 files; live spec skipped by default) |
| `auth-svc` `tsc --noEmit --incremental false` | exit 0 |
| `auth-svc` schema e2e | 8 tables alphabetically + `idx_outbox_pending` |
| outbox e2e | 7 cases: one row per registration, exact envelope/payload, 409 rollback writes nothing, publish marks `published`, a throw leaves `attempts=1` + `locked_until`, five failures park `failed` and a sixth drain ignores it, a held advisory lock returns `skipped` with the row untouched |
| live proof (`RUN_KAFKA_E2E=1`) | one record on `user.registered`, `key = userId`, `parseEventEnvelope` passes, no `email` key and no `@` in the payload, row `published` with `published_at` |
| `ecom-infra` `pnpm verify` / `topics:smoke` | 31/31, 28/28 |
| commit | `auth-svc` `5f22a2a`; `ecom-messaging` `ee88bfe` (its first commit — the repo had no `.git`) |

## Open

- Committed on 2026-10-31 with `auth-svc` `5f22a2a`. The gate re-run that day was lint (0/0,
  58 files), 29 unit tests in 10 files and `nest build`; e2e was **not** re-run because the
  compose stack was down, so the 45 + 1 skipped above is the 2026-10-30 run.
- ord-011 makes order-svc the third adopter and cuts `@ecom/messaging` 1.0.0.
- Outbox retention/archival is unplanned: `auth.outbox` grows for the life of the database while
  the topic keeps 7 days.
- No metrics endpoint: alerting on `failed` count, oldest-pending age, and a long-held relay lock
  is still manual.
- au-005 is still required before notify can email a new user.
- `RUN_KAFKA_E2E` set in a reused shell silently runs the live spec inside `pnpm test:e2e`; both
  live specs now scope the relay store to their own aggregate, but the variable is still ambient.
