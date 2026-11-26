# sf-076 — Theme, nav, page-settings and every BFF body are validated with contract zod schemas; /api/orders limit is clamped; dead import removed

- Repo: `storefront-ui`
- Phase: P0 · priority: P1 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 161323c
- Verified: 2026-11-26

## What

Theme, nav, page-settings and every BFF body are validated with contract zod schemas; /api/orders limit is clamped; dead import removed.

## Why

A wrong-shaped 200 must not be treated as success. Rejected: trusting backend types at runtime.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- None.
