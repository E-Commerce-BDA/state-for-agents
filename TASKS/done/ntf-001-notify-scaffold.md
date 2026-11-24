# ntf-001 — notify-svc scaffold, spec and Postgres schema (done, 2026-11-25)

- Repos: `notify-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: none
- Started: 2026-11-25 | Finished: 2026-11-25

## What

First commit in the new `notify-svc` repo: Nest 12 on port 4080, the shared
Postgres instance, a `notify` schema with `email_logs` and `processed_events`,
and health probes. No Kafka consumer and no SQS worker yet — those are
`ntf-002` and `ntf-003`.

`Documentation/services/notify.md` was written first, in the auth.md shape:
port, schema, transport rules, health contract, and the rule that an address is
resolved through auth-svc's internal lookup rather than carried on Kafka.

## Why

The scaffold is verifiable without a broker or SMTP, so it can be checked before
the event and task paths exist. Postgres holds an audit trail and a dedupe
claim; Mongo would add nothing for that shape. `reminder.dispatch` is absent:
`cart.abandoned` plus the send-email queue already cover reminders.

The migration is deliberately **not applied**. The local Postgres is not
available, and applying a schema change from this session without that stack
would be a guess. The SQL file is the artifact; a future task applies it when
the database is up.

## How

- `git init -b master`, origin `https://github.com/E-Commerce-BDA/notify-svc.git`,
  author preserved, nothing pushed.
- Config copied from the analytics-svc scaffold and adapted from Mongo to
  Postgres; local tarballs contracts 1.16.0 and messaging 0.5.0.
- `src/db/pool.ts` with bounded connection/query timeouts and an error listener;
  `src/db/schema.ts` is pure data checked against `db/001-notify-schema.sql`.
- Health follows auth-svc: liveness touches nothing, readiness returns the
  verbatim `not_ready` object on failure, both outside `/api/v1`.
- Commits: `a20a6bd` (service), `e8d34c2` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 7 tests / 2 files |
| `pnpm test:e2e` | 2 tests / 1 file (readiness reports 503 without Postgres) |
| `pnpm lint` / `pnpm build` | green |

`class-transformer` and `class-validator` were added after the first e2e run
showed ValidationPipe needs them; the rerun was green.

## Follow-ups

- Apply `db/001-notify-schema.sql` to the local `ecom` database when Postgres is up.
- `ntf-002` consumes four Kafka events; `ntf-003` runs the SQS send-email worker.
