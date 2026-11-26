# ca-014 — cart-svc: append-only audit with a least-privilege role

- Repo: `cart-svc`
- Phase: P2 · priority: P1 · kind: feature
- Started: 2026-10-31 · Finished: 2026-11-26
- Commits: `1f93bf7` (code, earlier wave); no new commit — verification found no defect
- Verified: **2026-11-26 against live Postgres**

## What

The `NOLOGIN`, non-superuser `cart_app` role has `USAGE` on schema `cart`, CRUD
on the seven operational tables, and only `SELECT, INSERT` on `cart.settings_audit`.
`db/005-cart-settings-audit-role.sql` grants that shape and revokes wider grants
first, so a re-run repairs rather than merely succeeds.

## Verification (live)

- Migration applied to `ecom-pg` with `ON_ERROR_STOP=1`: exit 0.
- `SET LOCAL ROLE cart_app` probe: `SELECT=t, INSERT=t, UPDATE=f, DELETE=f` on
  `cart.settings_audit`; both `UPDATE` and `DELETE` returned `permission denied
  for table settings_audit`. Probe rows were rolled back.
- Operational probe under the same role: INSERT+SELECT on the audit table,
  UPDATE on `settings`, INSERT/DELETE on `processed_events` all succeeded — the
  role can do its job, not only be denied.
- `test/audit-role.e2e-spec.ts`: 3/3 passed (append+read, reject UPDATE, reject
  DELETE). Full e2e twice: 13 files passed, 2 Kafka files skipped by config;
  99 tests passed, 2 skipped.
- Idempotency: immediate re-run exit 0, `relacl` unchanged and exactly one
  `pg_auth_members` row. Widening `UPDATE, DELETE` then re-running 005 restored
  `may_update=f, may_delete=f` and the documented `relacl`.
- Gates: `pnpm test` 19 files / 125 tests, lint, typecheck, build — all green.

## Caveat

`cart_app` is `NOLOGIN`, so the suite cannot connect *as* that role. The audit
assertions run under `SET LOCAL ROLE cart_app`; the other e2e specs run under the
login role `ecom`, with a direct restricted-role CRUD probe compensating. This
is the documented mechanism, not a gap in the assertions.

## Follow-ups

- None.
