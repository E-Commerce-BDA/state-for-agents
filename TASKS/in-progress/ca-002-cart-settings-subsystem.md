# ca-002 — Cart settings subsystem (in progress; schema applied)

## What

Add the registry-driven settings document, admin API, versioning, audit,
and route security that let an admin change `guestMergeStrategy` without a
rebuild. This is the dependency for `ca-004` merge policies.

## How

- `cart-svc/db/002-cart-settings.sql` — `cart.settings` +
  `cart.settings_audit`, seed `global` with `ON CONFLICT DO NOTHING`.
- `src/settings/settings.registry.ts` — keys, Zod schemas, defaults, UI
  metadata, visibility, permission.
- `src/settings/settings.repository.ts` — read, versioned update, audit
  insert in one transaction.
- `src/settings/settings.service.ts` — resolve defaults + overrides,
  validate, reset, version conflict.
- `src/settings/settings.controller.ts` — admin GET/PATCH; no public route.
- `src/common/guards/jwt-auth.guard.ts`, `roles.guard.ts` — verified JWT +
  `admin`.
- `test/settings.*` — defaults, overrides, unknown key, invalid value,
  reset, 409, audit, 401/403, no-store.

## Decisions

- Store overrides as JSONB, not one column per setting — new settings need
  no DDL. Rejected: typed columns (migration per setting).
- Keep defaults in code, not seed rows — a new setting works immediately.
  Rejected: seed every default (stale rows, overwrite risk).
- Require `version` on PATCH — two admins must not silently overwrite.
  Rejected: last-write-wins.
- Enforce `admin` role now; add `cart.write` when permissions are seeded.
  Rejected: blocking the API on an empty permission catalogue.

## Verification

Schema slice done 2026-10-27:

- `002-cart-settings.sql` applied to local `ecom-pg` (PG 16.15): two tables,
  three indexes including `one_active_cart_per_session`, and
  `trg_cart_settings_updated_at` present.
- Seed row `global` exists with `{}` / version `0`; audit is empty.
- Re-running `002` is idempotent (`INSERT 0 0`) and preserves an existing
  `guestMergeStrategy` override plus version.
- Transactional checks confirmed the unique guest-session index and JSONB
  object check; the test rows were rolled back.
- cart-svc commit: `c3a7f2a`.

Code slice pending. Gate: registry, repository, service, controller, JWT +
`admin` guards, unit + e2e green, `tsc --noEmit`, `oxlint`, `nest build`.
