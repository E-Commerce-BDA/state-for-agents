# anl-001 — analytics-svc scaffold and Mongo TTL schema (done, 2026-11-23)

## What

First commit in the new `analytics-svc` repo. Stands up a Nest 12 service on
port 4060 with a Mongo connection, three collection/index declarations, health
probes, and a service spec in the Documentation repo.

## How

- Repo initialised with `git init -b master`, origin
  `https://github.com/E-Commerce-BDA/analytics-svc.git`, author preserved.
- Pinned local tarballs: `@ecom/contracts` 1.16.0, `@ecom/messaging` 0.5.0.
  Install uses `pnpm install --ignore-workspace` because the root workspace
  config otherwise swallows the install (same as ecom-infra).
- `src/db/indexes.ts` is pure data: `page_views` TTL 30d, `cart_events` TTL 60d,
  `processed_events` unique `eventId` and **no TTL**. `IndexesService` applies
  it at boot; unit test asserts the windows without a DB.
- `HealthService` gives liveness (no dependencies) and readiness (Mongo ping,
  2s timeout). Health routes sit outside `/api/v1`.
- Docs-first: `Documentation/services/analytics.md` written in auth.md shape
  before code depended on the port/collections.

## Decisions (+ one rejected alternative each)

1. **No TTL on processed_events** — dedupe must outlive the facts it protects,
   or a replay after 30 days double-counts a view. Rejected: a 30d TTL for
   symmetry, which would silently break dedupe.
2. **Copy cms-svc's Vitest config instead of `nest new`** — default Nest
   generates Jest and would need conversion. Rejected: generate then convert.
3. **Fail fast with `retryAttempts: 0`** — a service with no Mongo must not
   report green while collecting nothing. Rejected: silent retry loops.

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 10 tests / 4 files green |
| `pnpm test:e2e` | 3 tests / 2 files green (skip paths; local Mongo down) |
| `pnpm lint` / `pnpm build` | green |

Pushed to `origin/master` as `4dc46e0`. Docs commit in Documentation:
`bdb3dcb`.
