# doc-007 — Rewrote stale payload examples and field docs against contracts 1.17.0.

- Repos: Documentation
- Commit(s): ade90d2
- Closed: 2026-11-26

## What

Rewrote stale payload examples and field docs against contracts 1.17.0.

## Why

Examples that fail the current strict schemas mislead builders.

Rejected: Rewriting historical task logs.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups


