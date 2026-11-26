# sf-075 — Failure envelope carries code, message, details and retryAfter end-to-end; outages are no longer shown as empty or 404

- Repo: `storefront-ui`
- Phase: P0 · priority: P0 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 5d5327d
- Verified: 2026-11-26

## What

Failure envelope carries code, message, details and retryAfter end-to-end; outages are no longer shown as empty or 404.

## Why

An outage must never look like the shopper lost data or that a page does not exist. Rejected: more generic toasts.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Admin happy path and review POST happy path need a seeded admin user/delivered order.
- Screenshot baseline diff from wave 1 still needs a refresh.
