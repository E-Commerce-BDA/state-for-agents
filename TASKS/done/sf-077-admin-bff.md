# sf-077 — Twelve role-guarded admin proxy routes forward to cms/catalog/auth with HttpOnly cookies, plus one public versioned config read

- Repo: `storefront-ui`
- Phase: P5 · priority: P1 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 498a075
- Verified: 2026-11-26

## What

Twelve role-guarded admin proxy routes forward to cms/catalog/auth with HttpOnly cookies, plus one public versioned config read.

## Why

The admin app must never hold service tokens; the storefront shell needs the same config as admin. Rejected: browser-to-service calls or an admin-only config route.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Some upstream paths may need one-line adjustment when admin endpoints land.
- Admin happy path not browser-tested; 401/403 guard confirmed.
