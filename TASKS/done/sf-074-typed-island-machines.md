# sf-074 — Eleven typed reducers replace implicit booleans in cart, wishlist, compare, checkout, search, listing, orders, address book, navbar, overlay and PDP islands

- Repo: `storefront-ui`
- Phase: P0 · priority: P0 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): e44e197
- Verified: 2026-11-26

## What

Eleven typed reducers replace implicit booleans in cart, wishlist, compare, checkout, search, listing, orders, address book, navbar, overlay and PDP islands.

## Why

Partial transitions caused the cold-checkout bounce, lost optimistic writes and silent failures. Rejected: XState; pure reducers fit the pure-lib rule.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Remaining runtime-only suspects A-S1/S2/S3 were browser-checked and pass.
