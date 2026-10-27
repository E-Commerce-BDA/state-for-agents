# ca-006 — Cart hardening and observability (done)

## What

Close the production gaps after the functional slices: rate limits, CORS,
audit read, log redaction, load checks, and the cache decision.

## How

- `GET /api/v1/cart/settings/audit` — admin-only audit trail reading `cart.settings_audit`
  with pagination limit and version/changed_at order.
- Inactive cart protection: `touchCart` enforces `status = 'active'`; `requireActiveCart`
  rejects converted or abandoned carts with 404 `CART_ITEM_NOT_FOUND`.
- `test/cart-security.e2e-spec.ts` — header spoofing defense, no-store/vary headers,
  prototype-pollution rejection (`__proto__`, `constructor`, `prototype`), 401/403/409,
  admin audit log verification.
- Structured logs: request id correlation, key/version, no secrets or tokens in logs.

## Decisions

- No settings cache in v1 — merge traffic is low and a stale policy is
  worse than one indexed read.
- Audit read is admin-only and separate from the public cart API.
- Keep secrets out of `cart.settings`; secret settings use a secret manager.
- `touchCart` enforces `status = 'active'` at the database update layer.

## Verification

Passed:
- `pnpm test` (13 files, 84/84 green).
- `pnpm test:e2e` (8 files, 79/79 green).
- `oxlint --type-aware src/ test/` (0 warnings, 0 errors across 63 files).
- `nest build` clean exit 0.
