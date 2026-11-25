# ca-013 — catalog outage counter (done, 2026-11-25)

- Repos: `cart-svc` (+ `Documentation`)
- Phase: P5 | priority: P1 | kind: chore | transport: http
- Started: 2026-11-25 | Finished: 2026-11-25

## What

`HttpCatalogClient.fail()` increments `catalogUnavailable`, and a guarded
`GET /api/v1/cart/internal/catalog-metrics` exposes the count with no-store.
The choke point covers timeout, 5xx, non-JSON and shape-invalid responses; a
well-formed response with no row stays a 422 and is not an outage.

## Why

The 503 was only in a log line, so an operator could not tell how many of the
cart's errors were the catalog versus itself. Counting in the client's single
failure path guarantees one increment per failed add without changing the
response body. A separate route keeps the HTTP dependency counter distinct
from the consumer counters added in ca-012.

## How

- `src/cart/catalog-metrics.ts` — injectable counter and snapshot.
- `src/cart/catalog-metrics.controller.ts` — guarded read route.
- `HttpCatalogClient` — injects the counter and increments in `fail()`.
- `CartModule` — provides counter and controller.
- Commits: `546b38e` (service), `bfce373` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 125 tests / 19 files |
| `pnpm lint` / `pnpm build` | green |

E2E could not run: Postgres is unavailable.

## Follow-ups

The storefront stale/fallback counter remains named debt.
