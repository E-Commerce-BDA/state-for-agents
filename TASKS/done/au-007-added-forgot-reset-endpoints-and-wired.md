# au-007 — Added forgot/reset endpoints and wired the storefront form.

- Repos: auth-svc
- Commit(s): a5d19fa + 4f1c187
- Closed: 2026-11-26

## What

Added forgot/reset endpoints and wired the storefront form.

## Why

A one-time fingerprinted token keeps email out of Kafka events.

Rejected: Returning the token in the 202 response.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- No email delivery path yet; link is not delivered. Migration e2e needs Postgres.
