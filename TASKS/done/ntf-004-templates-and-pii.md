# ntf-004 — templates, PII resolution and tests (done, 2026-11-25)

- Repos: `notify-svc`, `ecom-contracts` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: http
- Started: 2026-11-25 | Finished: 2026-11-25

## What

Four email renderers live in `src/templates/`: `welcome`,
`order-confirmation`, `cart-abandoned` and `status-update`. Each declares the
variables it needs. Missing variables throw in tests; in production the renderer
sends a short generic body and logs only the template id and missing key names,
never their values. Both the consumer and the worker use these functions, so
subjects cannot drift between the enqueue log and the sent message.

`order.status.updated` now emits its own `status-update` job. That required a
backwards-compatible fourth value in `emailTemplateSchema`, released as
contracts 1.17.0; existing payloads still validate. Added
`POST /api/v1/admin/test-email` behind `x-service-key`, which enqueues a test job
through the SQS path and returns 202 without ever accepting an address.

## Why

A broken template must be loud in tests and safe in production: empty
substitutions could silently send a blank or misleading email, and logging
variable values could put an address in a log line. The workaround of reusing
`order-confirmation` for status changes was a documented gap, not a design; the
acceptance calls for four templates. The support endpoint uses the service key
because notify has no user store and the worker remains the only address
resolver through au-005.

## How

- `src/templates/index.ts` — four pure renderers and `renderTemplate`.
- `consumer/handlers.ts` emits `status-update`; `email-sender.service.ts`
  renders through the shared module.
- `src/admin/` — controller, module and service-key guard.
- contracts 1.17.0: enum, jobs test, CHANGELOG, packed tarball; notify repinned.
- Commits: `57bae92` (contracts), `808c5a2` (notify), `ed610cc` (Documentation).

## Verification

| Check | Result |
|---|---|
| contracts typecheck / tests | green / 164 tests |
| notify `npx tsc --noEmit` | green |
| notify `pnpm test` | 33 tests / 6 files |
| notify `pnpm test:e2e` | 2 tests / 1 file |
| notify `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply the migration when Postgres is available.
- Live SMTP/LocalStack verification remains outstanding.
- A richer status notice needs a status field in SendEmailJob (contracts change).
