# cat-001 — Phase 1 & 2: Base foundation, DB connection, health probes, schema migration (done)

## What

Scaffolded `catalog-svc` (`:4020`), established bounded PostgreSQL pool connection (`:5433`), implemented `/health` and `/health/ready` probes, applied `catalog` DDL schema with 13 tables, partial indexes, and seeded fixture data.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2`.
- CLI-first scaffolding per `SKILL-NEST-CLI.md`: `pnpm exec nest g mo <name>`, co-located controllers and services with `--no-spec`, `.js` extension import discipline.
- PostgreSQL pool in `src/db/pool.ts` with 5s connection and 10s query bounded timeouts.
- Health probes in `src/health/` (`/health` fast liveness, `/health/ready` database probe returning 503 on drop).
- DDL schema in `db/001-catalog-schema.sql` (13 tables, GIN search vectors, navbar partial index, triggers).
- Seed data in `db/002-seed-catalog.sql` aligning with `cart-svc` fixtures (`TEE-MAIN`, `MUG-001`, `LAMP-DISC`).
- Test suites: unit (`src/health/health.service.spec.ts`, `src/db/pool.spec.ts` - 12 tests) and e2e (`test/health.e2e-spec.ts`, `test/schema.e2e-spec.ts` - 16 tests).

## Decisions

- CLI-first structure per `SKILL-NEST-CLI.md` for consistent module registration.
- Bounded pool timeouts (5s connect, 10s query); no process exit on pool error.
- Liveness returns 200 without DB probe; readiness verifies DB query and returns 503 on drop.
- Schema qualified with `catalog.` schema; raw SQL via `pg` pool (no ORM).
- Partial indexes on `categories` (`idx_categories_navbar`) and `products` (`idx_products_active`) to optimize hot storefront reads.

## Verification

- Vitest unit suite: 12/12 passed (3 test files).
- Vitest e2e suite: 16/16 passed (2 test files: health probes & schema constraints).
- Oxlint: 0 warnings, 0 errors across 29 files.
- Nest build: clean compilation (exit code 0).
