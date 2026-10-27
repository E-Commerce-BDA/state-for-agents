# cat-001 — Phase 1: Base foundation, DB connection, health probes, schema migration (in-progress)

## What

Scaffold `catalog-svc` (`:4020`), establish bounded PostgreSQL pool connection (`:5433`), implement `/health` and `/health/ready` probes, and apply `catalog` DDL schema with partial navbar index.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2`.
- CLI-first scaffolding per `SKILL-NEST-CLI.md`: `nest g mo <name>`, co-located controllers and services with `--no-spec`, `.js` extension import discipline.
- PostgreSQL pool in `src/db/pool.ts` with 5s connection and 10s query bounded timeouts.
- Health probes in `src/health/` (`/health` fast liveness, `/health/ready` database probe).
- DDL schema in `db/001-catalog-schema.sql` and seed in `db/002-seed-catalog.sql`.
- Test suites: unit (`src/health/health.service.spec.ts`, `src/db/pool.spec.ts`) and e2e (`test/health.e2e-spec.ts`, `test/schema.e2e-spec.ts`).

## Decisions

- CLI-first structure per `SKILL-NEST-CLI.md` for consistent module registration.
- Bounded pool timeouts; no process exit on pool error.
- Liveness returns 200 without DB probe; readiness verifies DB query and returns 503 on drop.
- Schema qualified with `catalog.` schema; raw SQL via `pg` pool (no ORM).

## Verification

Pending. Gate: unit + e2e green, `oxlint --type-aware`, `nest build`.
