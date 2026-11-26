# adm-002 — New Next 16 admin repo with 13 config screens, a storefront-only BFF bridge, admin-role guard, CSRF/SameSite handling and component trios

- Repo: `admin-app`
- Phase: P6 · priority: P2 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 17aec51, 731e2dc
- Verified: 2026-11-26

## What

New Next 16 admin repo with 13 config screens, a storefront-only BFF bridge, admin-role guard, CSRF/SameSite handling and component trios.

## Why

A second frontend must follow the same constitution and never hold service tokens. Rejected: admin routes inside the storefront.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Review moderation and theme preview/A-B deferred until endpoints exist.
- Admin happy path not integration-tested; coded to the agreed BFF contract.
