# ord-013 — Named stock-shortfall lines in the 409 and highlighted them in checkout.

- Repos: order-svc
- Commit(s): 84bf09a + 7fb1691
- Closed: 2026-11-26

## What

Named stock-shortfall lines in the 409 and highlighted them in checkout.

## Why

Structured ids beat parsing prose across two service boundaries.

Rejected: A new status code that clients do not branch on.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups


