# ca-002 — Cart settings subsystem (done, 2026-10-27)

## What

Add the registry-driven settings document, admin API, versioning, audit,
and route security that let an admin change `guestMergeStrategy` without a
rebuild. This is the dependency for `ca-004` merge policies.

## How

- `cart-svc/db/002-cart-settings.sql` — `cart.settings` +
  `cart.settings_audit`, seed `global` with `ON CONFLICT DO NOTHING`, and
  the missing `one_active_cart_per_session` index.
- `src/settings/settings.registry.ts` — keys, Zod schemas, defaults, UI
  metadata, visibility, permission.
- `src/settings/settings.repository.ts` — read, versioned update, audit
  insert in one transaction under `SELECT ... FOR UPDATE`.
- `src/settings/settings.service.ts` — resolve defaults + overrides,
  validate, reset, version conflict.
- `src/settings/settings.controller.ts` — admin GET/PATCH; no public route;
  `Cache-Control: no-store` + `Vary: Authorization`.
- `src/auth/*` — duplicated protocol constants, local JWT verification,
  roles metadata, and `admin` enforcement.
- `src/common/*` — shared error envelope and request-id extraction.
- `src/cart/cart.module.ts` — imports `SettingsModule` and registers the
  `APP_FILTER`; the existing cart controller/service stubs are preserved.
- `test/settings.e2e-spec.ts`, `test/schema.e2e-spec.ts` — settings HTTP
  behavior, six-table schema, seed, constraints, trigger, guest-session
  uniqueness.
- `src/**/*.spec.ts` — registry, service, JWT guard, roles guard, filter.

## Decisions

- Store overrides as JSONB, not one column per setting — new settings need
  no DDL. Rejected: typed columns (migration per setting).
- Keep defaults in code, not seed rows — a new setting works immediately.
  Rejected: seed every default (stale rows, overwrite risk).
- Require `version` on PATCH — two admins must not silently overwrite.
  Rejected: last-write-wins.
- Preserve unknown stored keys during a save — a rollback to older code
  must not delete a newer setting. Rejected: rewriting the document to only
  the current registry keys.
- Enforce `admin` role now; add `cart.write` when permissions are seeded.
  Rejected: blocking the API on an empty permission catalogue.
- Register the error envelope with `APP_FILTER` in `CartModule`, not only
  in `main.ts` — the e2e apps build `AppModule` directly. Rejected:
  bootstrap-only filter registration.
- No public settings endpoint and no secrets in `cart.settings` — settings
  are runtime behavior, not credentials. Rejected: exposing defaults for
  storefront bootstrapping (leaks admin policy surface).

## Verification

- `pnpm test`: 48 unit tests across 8 files green.
- `pnpm test:e2e`: 26 e2e tests across 4 files green.
- `pnpm exec tsc --noEmit`, `pnpm lint` (0 warnings), `pnpm build`: clean.
- Settings e2e covers 401/403, seeded defaults, valid PATCH, reset, unknown
  key, invalid value, stale-version 409, audit rows, `no-store`, and
  `Vary`; the local row is restored and test audit rows are deleted.
- Schema e2e covers six tables, ten indexes, the global seed, the JSONB
  object check, the settings `updated_at` trigger, and guest-session
  uniqueness.
- Post-run local DB check: `global` / `{}` / version `0`; zero
  `settings-e2e-*` audit rows.
- cart-svc commits: `c3a7f2a` (schema) plus `e83e0ee..e908a57` (25 code and
  test commits). All remain local; nothing pushed.

## Follow-ups

- Commit the existing uncommitted `cart-svc/src/app.module.ts` wiring
  (`CartModule` import + `JWT_SECRET` validation); HEAD's `AppModule` does
  not import `CartModule` yet, so the working tree is green but the commit
  chain alone is not fully wired.
- Enforce append-only audit with a least-privilege DB role; the local
  `ecom` owner can still update/delete audit rows.
- Add the `cart.write` permission check when the permission catalogue
  exists; the current gate is the `admin` role.
