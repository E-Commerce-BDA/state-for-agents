# ca-001 — Cart foundation (done, 2026-10-26)

## What

Established `cart-svc` as a runnable Nest 12 service with a crash-proof
Postgres pool, liveness/readiness probes, and the first cart schema. This
gave the service a stable base before cart CRUD and settings work.

## How

- `cart-svc/` Nest scaffold, ESM, port 4030, `/api/v1` global prefix with
  `/health` + `/health/ready` excluded.
- `src/db/pool.ts` — pooled `pg` connection with error handling, connect
  timeout, and release discipline.
- `src/health/*` — liveness never touches Postgres; readiness probes the DB
  and returns `503` with a minimal body on failure.
- `db/001-cart-schema.sql` — `cart.carts`, `cart.cart_items`,
  `cart.wishlists`, `cart.wishlist_items`; partial unique active-cart index;
  `NULLS NOT DISTINCT` line-item uniqueness; `set_updated_at()` triggers.
- `test/schema.e2e-spec.ts`, `test/health.e2e-spec.ts`,
  `test/db-resilience.e2e-spec.ts` — schema, probes, pool failure paths.

## Decisions

- Raw parameterized SQL via `pg`, no ORM — matches the project rule and
  keeps index/transaction behavior explicit. Rejected: Prisma (hidden SQL,
  migration runner conflict).
- Readiness checks Postgres but not Redis/Kafka yet — those dependencies are
  not wired into cart mutations in Phase 1. Rejected: checking everything
  now (would make readiness fail for unused dependencies).
- Keep cart item display fields as snapshots — no cross-schema joins to
  catalog. Rejected: join catalog on every cart read (couples services and
  breaks when catalog is absent).
- Apply `001-cart-schema.sql` manually in v1 — no migration runner.
  Rejected: adding a migration tool before the schema stabilizes.

## Verification

- 12 unit tests + 12 e2e tests green.
- `oxlint` 0 errors / 0 warnings; `nest build` clean.
- Local `ecom-pg` (:5433) applied 4 tables, 7 indexes, 2 triggers.
- Commits `994e88f..618a9a0` (23 local commits).
