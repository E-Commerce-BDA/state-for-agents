# srch-006 — Added a guarded trending endpoint for the search palette.

- Repos: search-svc
- Commit(s): 042998f
- Closed: 2026-11-26

## What

Added a guarded trending endpoint for the search palette.

## Why

Curated data should come from the existing index, not a new ranking table.

Rejected: A persisted ranking table or a browser-held service key.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Live endpoint verification needs search-svc running.
