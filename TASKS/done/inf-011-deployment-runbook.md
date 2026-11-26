# inf-011 — Documented a one-instance AWS deployment (Lightsail vs EC2 t3.micro), SSM secrets, TLS, Nginx edge, backups and rollback; pinned the real admin image digest

- Repo: `ecom-infra`
- Phase: P5 · priority: P2 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): 55b5aeb, 29830d7, 2567b88
- Verified: 2026-11-26

## What

Documented a one-instance AWS deployment (Lightsail vs EC2 t3.micro), SSM secrets, TLS, Nginx edge, backups and rollback; pinned the real admin image digest.

## Why

Deployment is a joint learning exercise, not an execution here. Rejected: Fargate for v1 cost.

## Verification

Coordinator verified the commit(s), clean trees and author identity. Each repo's
own gates were rerun: storefront lint 0 errors / 42 advisory, typecheck clean,
1415 tests in 192 files, webpack build green; catalog 186 unit + 9 e2e against
live Postgres; cms 233 unit + 110 e2e against live Mongo; admin 63 tests,
typecheck, lint and build green; infra 61 local tests and all static gates green.
Contracts 2.1.0 adds the optional fields cms-012 emits.

## Follow-ups

- Pricing must be confirmed at purchase time.
- Nothing was provisioned or deployed.
