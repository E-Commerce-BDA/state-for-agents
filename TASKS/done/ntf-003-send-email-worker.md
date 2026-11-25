# ntf-003 — SQS send-email worker with SMTP and DLQ (done, 2026-11-25)

- Repos: `notify-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: sqs-consumer
- Started: 2026-11-25 | Finished: 2026-11-25

## What

A long-poll worker consumes `notify-send-email` and sends through SMTP, with
Mailpit as the local target. It resolves each address through auth-svc's
internal lookup (`au-005`) using the service key, so no email sits in a Kafka
event or in the SQS payload. There is no Kafka involvement in the worker.

A unique `email_logs.idempotency_key` makes a redelivery a no-op. Every attempt
records status, attempts, `last_error` and the provider message id. SMTP and
lookup failures are recorded and rethrown so SQS redrives five times before its
DLQ. Guest carts have no user id, so their jobs are acknowledged and recorded
as failed with that reason rather than retried.

## Why

SQS owns task retries and dead-lettering; the worker resolves or throws, and
the transport decides what happens next. A Mailer port keeps the handler
testable without SMTP. Guest jobs are unfixable by retry, so five attempts
would only fill the DLQ with the same message.

The poller is opt-in (`SQS_TASKS_ENABLED=true`) so a local run without
LocalStack stays quiet; the producer remains available when it is off.

## How

- `src/tasks/mailer.ts` — Mailer port and nodemailer implementation.
- `src/tasks/auth-email.client.ts` — service-key lookup with a 2s timeout.
- `src/tasks/email-sender.service.ts` — dedupe, address resolution, send, log.
- `src/tasks/notify-worker.module.ts` — handler token for the dynamic module.
- `EventsModule` now supplies handlerToken and the enable predicate.
- Migration gained `provider_message_id`; still unapplied.
- Commits: `169cb8c` (service), `17b6f6b` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 24 tests / 4 files |
| `pnpm test:e2e` | 2 tests / 1 file (no LocalStack/SMTP needed) |
| `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply the amended migration when Postgres is available.
- ntf-004 adds templates and PII-aware tests.
- Live SMTP/LocalStack verification remains outstanding.
