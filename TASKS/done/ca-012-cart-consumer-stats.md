# ca-012 — cart consumer stats on an HTTP route (done, 2026-11-25)

- Repos: `cart-svc` (+ `Documentation`)
- Phase: P5 | priority: P1 | kind: feature | transport: http
- Started: 2026-11-25 | Finished: 2026-11-25

## What

`GET /api/v1/cart/internal/consumer-stats` behind `x-service-key` with
`Cache-Control: no-store`. It returns the nine shared counters beside `lag`,
`totalLag`, `lastCommit` and `sampledAt` — the same shape catalog and search
expose. The group was previously observable only with
`kafka-consumer-groups.sh`.

## Why

A lag without a last commit cannot distinguish "behind" from "stopped", which
is the question the endpoint exists to answer. The route reads the same
injectable `ConsumerMetrics` provider the handler uses, so the counters cannot
drift from actual commits. The lag sampler measures the group itself on a
separate admin connection: a broker it cannot reach is a missing sample, not a
stalled commit. Counters are operational, so the route is guarded and carries
no shopper data.

## How

- `src/events/consumer-metrics.ts` — injectable subclass, snapshot type and
  `buildConsumerStats`.
- `src/events/consumer-stats.controller.ts` — guarded route.
- `EventsModule` — metrics provider, lag sampler for `order.created`, handler
  factory now takes metrics; `AuthModule` imported for the guard.
- Commits: `5903ad8` (service), `2b44b82` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 122 tests / 18 files |
| `pnpm lint` / `pnpm build` | green |

E2E could not run: Postgres is unavailable and the existing suites need it.

## Follow-ups

- Live verification of the lag sample needs a broker.
