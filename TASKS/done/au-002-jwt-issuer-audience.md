# au-002 — JWT issuer/audience (done, 2026-10-27)

## What

Make `auth-svc` access tokens state their origin and intended audience, and
make the guard verify both. Today the token is signed with only `expiresIn`
and verified by signature alone, while `services/auth.md` P2 and
`services/cart.md` already require `issuer`/`audience` checks. This closes
the docs/code mismatch before the cart admin settings guard copies the same
contract.

## How

- `auth-svc/src/auth/auth.constants.ts` — protocol constants:
  `iss = ecom-auth`, `aud = ecom-api`, `HS256`, 30-second tolerance.
- `auth-svc/src/auth/auth.module.ts` — add issuer, audience, and algorithm
  to `signOptions`; every access-token path already uses this module.
- `auth-svc/src/auth/guards/jwt-auth.guard.ts` — verify issuer, audience,
  pinned HS256, and 30-second clock tolerance.
- `auth-svc/src/auth/guards/jwt-auth.guard.spec.ts` — unit coverage for
  missing/invalid headers, valid token, wrong issuer, and wrong audience.
- `auth-svc/test/login.e2e-spec.ts` — decode the issued token and assert
  `iss`/`aud`.
- `auth-svc/test/me.e2e-spec.ts` — reject tokens with wrong or missing
  issuer/audience.
- `Documentation/services/auth.md` — pin the exact values in P2.
- `Documentation/services/cart.md` — pin the same values where the admin
  guard contract is described.

## Decisions

- **Constants, not environment variables** — issuer and audience are
  protocol values, not secrets; env would let auth-svc and cart-svc drift.
  Rejected: `JWT_ISSUER`/`JWT_AUDIENCE` env vars.
- **Verify HS256 and 30 seconds now** — the auth contract already promises
  both; adding only issuer/audience would leave algorithm and clock gaps.
  Rejected: signature + issuer/audience only.
- **Cart copies the constants** — no shared contracts package exists yet;
  duplicating four literals is safer than blocking on `ecom-contracts`.
  Rejected: waiting for a shared package.

## Verification

- `pnpm test`: 24 unit tests green (17 before + 7 guard tests).
- `pnpm test:e2e`: 37 e2e tests green (36 before + 1 issuer/audience test).
- `pnpm exec tsc --noEmit`, `pnpm lint`, `pnpm build`: clean.
- Login token asserts `iss=ecom-auth`, `aud=ecom-api`; wrong issuer,
  wrong audience, and missing claims return `401`.
- auth-svc commits: `791d094`, `c7fe3d0`, `3fad688`, `28f7df7`, `4b75f78`,
  `f31c0ed`; docs `a077481`, `3e53c9d`.

