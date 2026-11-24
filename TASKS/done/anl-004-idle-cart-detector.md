# anl-004 — idle-cart detector publishes cart.abandoned (done, 2026-11-24)

- Repos: `analytics-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: kafka-producer
- Started: 2026-11-24 | Finished: 2026-11-24

## What

A one-minute cron scans the latest active `cart_events` fact per cart and
publishes `cart.abandoned` for those quiet past the configured idle threshold
(default 30 minutes). The event goes into the existing Mongo outbox, keyed by
`userId`, or by `sessionId`/`cartId` for guests.

Exactly one event is emitted per cart per idle window. A marker keyed by
`<cartId>|<lastActivityAt>` in the new `abandonment_windows` collection is
inserted with the outbox row in one Mongo transaction; a duplicate marker means
the reminder already went out. A newer `cart.updated` changes the window and
allows a new event.

## Why

Envelope ids must be UUIDs, so a deterministic event id cannot carry the window
key. A marker collection makes the database decide idempotency and shares the
transaction with the event, so a crash cannot leave one without the other. A
plain scan-time flag would not have that atomicity.

Guests have no `userId`; keying only by it would silently drop them, so the
session id (or cart id) is used.

Rejected: `reminder.dispatch` — already absent from contracts, infra and docs,
and covered by `cart.abandoned` plus the notify send-email worker.

## How

- `src/abandonment/abandonment-writer.ts`: aggregation, marker insert and outbox
  write under `MongoTransactions`.
- `src/abandonment/abandonment.scheduler.ts`: cron, threshold, batch, enable flag.
- `src/abandonment/abandonment.module.ts`, wired into `app.module.ts` with
  `ScheduleModule.forRoot()`.
- `AnalyticsOutbox.recordCartAbandoned` added beside the page-view method.
- `abandonment_windows` declared with a unique `_id` and no TTL; the no-TTL
  rule matches `processed_events` so dedupe outlives the facts.
- Config: `CART_ABANDONED_AFTER_MS`, `ABANDONMENT_SWEEP_ENABLED`,
  `ABANDONMENT_SWEEP_BATCH_SIZE`.
- Commits: `e92e8f5` (service), `0854d57` (Documentation).

## Verification

- `npx tsc --noEmit` exit 0.
- `pnpm test`: 10 files / 43 tests passed (up from 9 / 33).
- `pnpm lint` and `pnpm build` exit 0.
- E2E not run: needs live Mongo/Kafka.

## Follow-ups

- notify-svc can consume `cart.abandoned` once it exists.
