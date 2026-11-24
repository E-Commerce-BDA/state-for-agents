# ca-011 — bound the order.created retry ladder to the broker session (done, 2026-11-24)

- Repos: `cart-svc`
- Phase: P3 | priority: P0 | kind: bug | transport: kafka-consumer
- Started: 2026-11-24 | Finished: 2026-11-24

## What

cart ran `@ecom/messaging` 0.3.0 with the default 1/2/4/8/16s ladder — 31s of
sleeps, longer than the 45s session that 0.5.0 sets explicitly once handler work
is counted. A member evicted mid-sleep gets `UNKNOWN_MEMBER_ID` on both the DLQ
write and the offset commit, so the group re-joins and replays the same record.

Repinned to the 0.5.0 tarball, moved every `@ecom/messaging/nest` import to the
narrow `/nest/consumer` and `/nest/outbox` entries, and passed `retryBudgetMs:
20_000` through a shared handler factory. The default ladder truncates to
1/2/4/8s — five attempts, 15s of sleeps.

## Why

This is ADR 44's failure mode, observed live on `order.created` while `srch-004`
was being verified. 20s mirrors search's reviewed value: 15s of sleeps leaves
the rest of the 45s session for the handler, the DLQ write and the commit.

The narrow entries were mandatory, not cosmetic. In 0.5.0 the `/nest` barrel
re-exports the SQS task module, which eagerly imports the optional
`@aws-sdk/client-sqs` peer. cart has no such peer, so a plain repin would fail at
boot.

A shared factory lets the regression test drive the production wiring rather
than a copy of it.

Rejected: raising the session timeout (moves the boundary without fixing the
ladder/session relationship); keeping `/nest` imports and adding the SQS peer.

## How

- 11 import sites moved to narrow entries.
- `RETRY_BUDGET_MS = 20_000` and `createOrderCreatedHandler()` exported from
  `src/events/events.module.ts`; the Nest provider calls the factory.
- New regression case in `cart-consumer.controller.spec.ts` injects `sleep` and
  a permanent transient failure, then asserts four sleeps totalling 15s, five
  attempts, one DLQ write and the commit.
- Commit `438372a` in `cart-svc`.

## Verification

- `npx tsc --noEmit` exit 0; `pnpm test` 17 files / 120 tests passed.
- `pnpm build` and `pnpm lint` exit 0.
- `pnpm test:e2e` cannot run here: `ECONNREFUSED ::1:5433` / `127.0.0.1:5433`
  from the absent Postgres stack. Confirmed by running a single e2e spec.

## Follow-ups

- The accumulated `order.created.dlq` records still need `inf-006`.
- cart still has no `/consumer-stats` route and no retention sweeper.
