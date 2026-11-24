# au-005 — internal email lookup for notify-svc (done, 2026-11-24)

- Repos: `auth-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: http
- Started: 2026-11-24 | Finished: 2026-11-24

## What

Added `GET /internal/users/:id/email`, also served at
`/auth/internal/users/:id/email`, behind the `x-service-key` header. The
response is exactly `{ userId, email }` with `no-store`; unknown ids return 404
in the shared error envelope and missing/wrong keys return 401 with
`SERVICE_KEY_INVALID`.

`INTERNAL_SERVICE_KEY` is mandatory at boot. UsersService projects the database
row down to the two fields, so password hashes, phone numbers, status and tokens
cannot leave through this route.

## Why

user.registered deliberately carries no email, so notify-svc needs a way from a
user id to an address. Adding the email to the event would put PII on Kafka and
break the test that asserts its absence. The admin profile endpoint exposes far
more than notify needs. A guarded route with a default development key would be
no guard at all.

## How

- `src/auth/guards/service-key.guard.ts`: missing/wrong key → 401
  `SERVICE_KEY_INVALID`.
- `src/users/users.service.ts`: `findIdEmail` projects the row and releases the
  client.
- `src/users/internal.controller.ts`: dual paths, guard, 404, no-store.
- `AuthModule` provides/exports the guard; `UsersModule` imports it.
- Joi `INTERNAL_SERVICE_KEY` added to the env schema; e2e config and the local
  `.env` carry a test key.
- Commits: `5323e28` (service), `f851c57` (Documentation).

## Verification

- `npx tsc --noEmit` exit 0.
- `pnpm test`: 11 files / 35 tests passed.
- `pnpm lint` and `pnpm build` exit 0.
- E2E not run: Postgres unavailable, requests fail before the app boots.

## Follow-ups

- notify-svc can now resolve addresses once it exists.
- auth-svc has all four of its tasks done.
