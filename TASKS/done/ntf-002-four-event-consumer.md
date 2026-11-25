# ntf-002 — consume four events into idempotent email jobs (done, 2026-11-25)

- Repos: `notify-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: kafka-consumer
- Started: 2026-11-25 | Finished: 2026-11-25

## What

notify-svc subscribes to `order.created`, `cart.abandoned`, `user.registered`
and `order.status.updated` on one group named exactly `notify-svc`. Each event
becomes one `notify-send-email` SQS job. No Kafka events are published and no
SMTP is sent here — the worker is ntf-003.

The claim in `notify.processed_events` and an `email_logs` row commit in one
Postgres transaction. The job is enqueued after commit with `event:<event id>`
as its idempotency key. If SQS refuses, both are compensated for redelivery;
if commit fails after enqueue, the worker's unique key drops the duplicate.

## Why

SQS cannot join a Postgres transaction, so a single atomic "claim plus enqueue"
is impossible. The durable claim prevents duplicate enqueues and the worker's
unique key prevents duplicate sends — together they cover both failure orders.
In-memory dedupe would not survive a restart.

The SQS module is producer-only: an enabled poller with no handler is a
declaration-time boot error. `order.status.updated` reuses the
`order-confirmation` template because the contract defines only three
templates; a fourth is a contracts change, and the key keeps it distinct.

## How

- `src/consumer/`: runtime, four `@EventPattern` routes, handler with payload
  parsing and the claim/log transaction, task publisher, provider module.
- `db/001-notify-schema.sql` and `src/db/schema.ts` gained `idempotency_key`
  with a unique index, a nullable `to_address` and an explicit `aggregate_id`.
  The migration is still unapplied.
- Added `@nestjs/microservices`, `kafkajs` and `@aws-sdk/client-sqs`.
- Commits: `0466281` (service), `afb54fc` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 18 tests / 3 files |
| `pnpm test:e2e` | 2 tests / 1 file (readiness 503 without Postgres) |
| `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply the amended migration when Postgres is available.
- ntf-003 sends email and resolves addresses through au-005.
- A dedicated status template belongs in a contracts change.
