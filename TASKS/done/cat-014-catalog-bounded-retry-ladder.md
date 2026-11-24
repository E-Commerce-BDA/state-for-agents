# cat-014 — bound the event retry ladder and reconcile the lockfile (done, 2026-11-24)

- Repos: `catalog-svc`
- Phase: P3 | priority: P0 | kind: bug | transport: kafka-consumer
- Started: 2026-11-24 | Finished: 2026-11-24

## What

catalog ran `@ecom/messaging` 0.3.0 with the same unbounded 31s ladder that wedged
search. Repinned to 0.5.0, moved the eight `@ecom/messaging/nest` imports to
`/nest/consumer` and `/nest/outbox`, and passed `retryBudgetMs: 20_000` through a
shared factory. Two regression cases cover the truncated ladder and the
first-attempt terminal path.

`pnpm install` also reconciled a pre-existing drift: `package.json` already
pinned `@ecom/contracts` 1.15.0 while `pnpm-lock.yaml` still resolved 1.9.0.

## Why

Same ADR 44 exposure as cart, on three topics: `order.created`, `product.imported`
and `order.status.updated`. One reviewed budget for all three consumers keeps the
protocol uniform; per-service values would let the next handler re-open the gap.

`translateError: dlqReason` stays ahead of the budget: a closed reservation or a
taken SKU is a deterministic answer, so it must dead-letter on attempt 1 rather
than walk a shorter ladder. Dropping the translator would turn a fast answer into
a slow one.

Keeping the lockfile reconciliation is correct — reverting it would leave the
lockfile disagreeing with the declared pin, and the next install would reintroduce
the same change.

## How

- `RETRY_BUDGET_MS = 20_000` and `createKafkaEventHandler()` exported from
  `src/events/events.module.ts`; `translateError: dlqReason` retained.
- New `event retry budget` describe block with a setup helper; asserts
  `[1000, 2000, 4000, 8000]`, five attempts, one dead letter and commit for a
  transient failure, and zero sleeps plus `reservation-closed` on attempt 1 for
  a `ReservationClosedError`.
- Commit `48efba7` in `catalog-svc`.

## Verification

- `npx tsc --noEmit` exit 0; `pnpm test` 25 files / 167 tests passed. The boot
  warning prints `5 configured delays reduced to 1000/2000/4000/8000 (4 retries)`.
- `pnpm build` exit 0; `pnpm lint` exit 0 with two pre-existing unused-import
  warnings in the untouched `src/products/variants.controller.ts`.
- E2E needs the live Postgres/Kafka stack and was not run.

## Follow-ups

- The DLQ backlog needs the replay task `inf-006`.
- STATUS §7 still listed the catalog cursor as carried debt; `cat-015` closed it
  on 2026-11-17, and this reconciliation corrects that line.
