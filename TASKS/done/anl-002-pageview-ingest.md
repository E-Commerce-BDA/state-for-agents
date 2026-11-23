# anl-002 — analytics page-view ingest and outbox producer (done, 2026-11-23)

## What

`POST /api/v1/analytics/track` accepts a storefront page-view beacon, validates
it, rate-limits it per session, and writes one `page.viewed` row into
`analytics_outbox`. It returns 202 immediately and publishes nothing
synchronously. This unblocks sf-052 (the storefront's `/api/track` beacon).

## How

- `trackEventSchema` is `pageViewedPayloadSchema` from contracts 1.16.0 with
  `timestamp` optional on the wire; the service overwrites it with server time.
- `ZodValidationPipe` copied from cms-svc but strips rejected values from error
  details, so a token in a page URL cannot leak into a response or log.
- `SlidingWindowLimiter` is a pure in-memory per-session window: 60 events /
  60s by default, configurable, with pruning and a hard cap on tracked
  sessions. 429 + `Retry-After` on rejection.
- `AnalyticsOutboxModule` uses `createMongoOutboxModule` from the narrow
  `@ecom/messaging/nest/outbox` entry; collection `analytics_outbox`, producer
  `analytics-svc`. `AnalyticsOutbox.record` validates the payload through the
  store and keys the event by `sessionId`.
- Added the Mongo connection binder and transaction helper the scaffold had
  deferred, because the outbox store needs a session for its write.
- Docs-first: `Documentation/services/analytics.md` HTTP section updated from
  planned to shipped before the commit.

## Decisions (+ one rejected alternative each)

1. **Validate → rate-limit → enqueue** — a bad body gets 400 and is not
   charged to the session. Rejected: rate-limit first (junk traffic could lock
   a legitimate session).
2. **Server timestamp** — a wrong client clock cannot skew funnels. Rejected:
   trusting the client; adding an event-id field to contracts.
3. **No value echo in 400s** — page URLs may contain tokens. Rejected: the
   default cms-svc pipe output, which can include the rejected value.
4. **No ingest dedupe** — the contract has no client event id; at-least-once
   delivery and `processed_events` dedupe are anl-003's job. Rejected: a new
   contract field and a MINOR release.

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 20 tests / 8 files green |
| `pnpm test:e2e` | 5 tests / 3 files green (skip paths; Mongo down) |
| `pnpm lint` / `pnpm build` | green |

Commits: analytics-svc `3b915d3`, Documentation `9f1e59d`.
