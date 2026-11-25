# cms-010 — Added expiring signed URLs for private media.

- Repos: cms-svc
- Commit(s): a1143e8
- Closed: 2026-11-26

## What

Added expiring signed URLs for private media.

## Why

A capability must still go through the one containment resolver.

Rejected: Widening the public media route.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Mongo e2e needs a live stack.
