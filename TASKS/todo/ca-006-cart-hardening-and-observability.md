# ca-006 — Cart hardening and observability (todo)

## What

Close the production gaps after the functional slices: rate limits, CORS,
audit read, log redaction, load checks, and the cache decision.

## How

- Nginx rate limit for `/api/v1/cart/settings` (5 req/s; writes 2/s) and
  cart mutations; CORS allowlist for the admin origin.
- `GET /api/v1/cart/settings/audit` — admin-only cursor feed.
- Structured logs: request id, key/version, no tokens or full values.
- `test/cart-security.*` — header spoofing, no-store, body limit,
  prototype-pollution keys, 401/403/409.
- Load check: cart read/removal P99 targets; merge concurrency.
- Decide cache: no cache in v1; if added, key by settings version.

## Decisions

- No settings cache in v1 — merge traffic is low and a stale policy is
  worse than one indexed read. Rejected: premature Redis cache.
- Audit read is admin-only and separate from the public cart API.
  Rejected: expose audit on the settings document.
- Keep secrets out of `cart.settings`; secret settings use a secret
  manager. Rejected: encrypting arbitrary JSONB in the app.

## Verification

Pending. Gate: security suite green; Nginx config reviewed; logs contain no
secrets; cache decision recorded.
