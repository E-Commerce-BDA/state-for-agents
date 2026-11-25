# doc-006 — Added a per-repo comment counter and baseline gate.

- Repos: Documentation
- Commit(s): 5fa282f
- Closed: 2026-11-26

## What

Added a per-repo comment counter and baseline gate.

## Why

A ratchet stops comment growth without banning reason-required comments.

Rejected: A CI hook or lint rule — explicitly out of scope.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Refresh the baseline after the wave's new comments are reviewed.
