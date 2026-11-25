# cms-009 — Made the SQS worker opt-in and broadened its integration.

- Repos: cms-svc
- Commit(s): ca4871c
- Closed: 2026-11-26

## What

Made the SQS worker opt-in and broadened its integration.

## Why

A default-on poller starts with no broker in development.

Rejected: Relying on the messaging default.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- LocalStack e2e needs a live stack.
