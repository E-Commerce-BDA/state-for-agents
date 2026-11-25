# ord-014 — Added a leader-locked sweep for stale captures and stuck refunds.

- Repos: order-svc
- Commit(s): e2b8a65
- Closed: 2026-11-26

## What

Added a leader-locked sweep for stale captures and stuck refunds.

## Why

Recovery should not depend on the customer retrying or an operator marking rows.

Rejected: Lease columns and a new scheduler dependency.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Real SQL claim/settlement paths and outbox publication need Postgres/Kafka.
