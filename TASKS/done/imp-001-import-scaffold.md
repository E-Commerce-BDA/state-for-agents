# imp-001 — import-svc scaffold, spec and Postgres schema (done, 2026-11-25)

- Repos: `import-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: none
- Started: 2026-11-25 | Finished: 2026-11-25

## What

First commit in the new import-svc repo: Nest 12 on port 4070, the shared
Postgres instance, an `import` schema with `import_jobs` and `import_rows`, and
health probes. No upload API, SQS producer or worker yet — those are imp-002
and imp-003.

`Documentation/services/import.md` was written first, in the auth.md shape:
port, schema, health contract, and the future transport ownership.

## Why

The batch report and per-row retries need relational state, so Postgres holds
`import_jobs` and `import_rows`; an in-memory CSV could not resume. `import_rows`
is uniquely keyed by `(job_id, row_number)` so a redelivered row task updates
one row instead of appending another.

The migration is deliberately **not applied**: local Postgres is unavailable,
and applying a schema change from this session without that stack would be a
guess. A unit test checks the SQL file against the pure declaration.

## How

- `git init -b master`, origin `https://github.com/E-Commerce-BDA/import-svc.git`,
  author preserved, nothing pushed.
- Config copied from the notify scaffold, adapted to import-svc and Postgres;
  local tarballs contracts 1.17.0 and messaging 0.5.0.
- `src/db/schema.ts` is pure data checked against `db/001-import-schema.sql`.
- Health follows auth and notify; both routes sit outside `/api/v1`.
- Commits: `c81a743` (service), `76946aa` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 7 tests / 2 files |
| `pnpm test:e2e` | 2 tests / 1 file (readiness 503 without Postgres) |
| `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply `db/001-import-schema.sql` to the local `ecom` database when Postgres is up.
- imp-002 adds the upload API and SQS row producer.
- imp-003 adds the worker and the `product.imported` publisher.
