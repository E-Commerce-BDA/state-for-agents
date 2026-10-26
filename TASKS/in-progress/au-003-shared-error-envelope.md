# au-003 — Shared error envelope (todo)

## What

Replace Nest's default error body in `auth-svc` with the shared envelope
already documented in `4.API-Design.md` §1.5:

`{error:{code,message,details?}, requestId, timestamp}`

This is needed so auth screens and the admin app can switch on a stable code
instead of parsing Nest's `statusCode/message/error` shape.

## How

- `auth-svc/src/common/filters/http-exception.filter.ts` — catch all
  exceptions, normalize the body, echo/generate `requestId`, and log only
  server-side failures.
- `auth-svc/src/app.module.ts` — register the filter with `APP_FILTER` so
  the e2e apps (which build the module directly) get the same behavior as
  `main.ts`.
- `auth-svc/src/common/filters/http-exception.filter.spec.ts` — unit tests
  for 400/401/500, custom codes, request-id echo/fallback, and the health
  probe exemption.
- `auth-svc/test/login.e2e-spec.ts` — assert the 401 envelope.
- `auth-svc/test/register.e2e-spec.ts` — assert the validation and
  duplicate-email envelopes.
- `auth-svc/test/me.e2e-spec.ts` — assert the 401 envelope.
- `auth-svc/test/admin.e2e-spec.ts` — assert the 403 envelope.

## Decisions

- **`APP_FILTER`, not `main.ts` only** — the e2e suites instantiate
  `AppModule` themselves; registering only in `main.ts` would leave the
  tests and any other bootstrap path unprotected. Rejected: global filter
  installed only in `main.ts`.
- **Status-derived codes in this slice** — `VALIDATION_FAILED`,
  `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`,
  `RATE_LIMITED`, `INTERNAL_ERROR`, `SERVICE_UNAVAILABLE`. Explicit
  `code`/`details` from an exception pass through, so cart settings can add
  `UNKNOWN_SETTING`/`SETTINGS_VERSION_CONFLICT` later. Rejected: editing
  every auth throw site for bespoke codes before the contracts package
  defines them.
- **Health probes stay raw** — readiness parses `{status, checks}`; the
  filter detects `/health` and returns the original body. Rejected:
  wrapping probes in the API envelope.
- **`x-request-id` echo with UUID fallback** — the gateway normally sets
  it, but local and direct calls must still work. Rejected: requiring the
  header and failing local requests.

## Verification

Pending. Gate: auth unit + e2e green, `tsc --noEmit`, `oxlint`, `nest
build`; 400/401/403/409/404/500 responses carry the envelope; readiness
`503` keeps its raw probe body.
