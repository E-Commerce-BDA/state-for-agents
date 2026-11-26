# cat-016 — Added POST /api/v1/catalog/products/:id/reviews with moderation state and admin list/moderation endpoints

- Repo: `catalog-svc`
- Phase: P0 · priority: P1 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 303628b
- Verified: 2026-11-26

## What

Added POST /api/v1/catalog/products/:id/reviews with moderation state and admin list/moderation endpoints.

## Why

The storefront UI posted to a route that did not exist and always failed. Rejected: hiding the UI.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- No public approved-review read endpoint in scope; no client idempotency key on POST.
