# cms-012 — Public config/sections responses carry configured/state metadata; a signed preview token admits inactive/draft reads

- Repo: `cms-svc`
- Phase: P5 · priority: P1 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 9e77dc3
- Verified: 2026-11-26

## What

Public config/sections responses carry configured/state metadata; a signed preview token admits inactive/draft reads.

## Why

Never-configured, cleared, missing and outage all produced the same 200 empty body; admins could not preview before publish. Rejected: breaking status codes or forcing publish.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Contracts 2.1.0 (107e6fc) makes the new fields optional; consumers must repin before CMS deploys. Verified paths: storefront and admin-app are on 2.1.0.
