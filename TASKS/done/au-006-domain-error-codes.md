# au-006 — domain error codes for token reuse and disabled accounts (done, 2026-11-25)

- Repos: `auth-svc`, `frontend/storefront` (+ `Documentation`)
- Phase: P4 | priority: P1 | kind: feature | transport: http
- Started: 2026-11-25 | Finished: 2026-11-25

## What

Four auth-svc 401 throws now carry `code: TOKEN_REUSED` or `code:
ACCOUNT_DISABLED` in the shared error envelope, with unchanged status and
message. The storefront client reads `error.code`, validates it with
`isAuthErrorCode`, and no longer lowercases `error.message` to classify a
refresh. An unknown code falls back to `TOKEN_EXPIRED`; login and register
remain generic.

## Why

Parsing prose across a service boundary breaks whenever copy changes and
cannot be type-checked. The filter already passes a payload `code` through, so
the fix was local to the throws and the client. Keeping the message unchanged
avoids an enumeration oracle at login, and keeping the status unchanged avoids
changing a contract. No message fallback was kept: the task explicitly removes
message parsing, and a stale deployment would simply preserve the bug.

## How

- `auth.service.ts` — four object-shaped UnauthorizedExceptions.
- `lib/auth/client.ts` — `readCode`, `classify(status, code, operation)`.
- Tests in both repos now feed codes instead of phrases.
- Commits: `b718e4a` (auth), `ea84c32` (storefront), `e6d1457` (Documentation).

## Verification

auth: tsc clean, 35 unit tests, lint, build. Storefront: tsc clean, lint 0
errors (40 advisory warnings), 1290 tests, webpack build. E2E as a whole needs
the absent Postgres.

## Follow-ups

A shared error enum in `@ecom/contracts` is a separate versioned change.
