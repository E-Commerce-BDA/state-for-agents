# sf-066 — Wired palette trending and curated cards from search-svc.

- Repos: storefront-ui
- Commit(s): 5425433
- Closed: 2026-11-26

## What

Wired palette trending and curated cards from search-svc.

## Why

The endpoint contract is already versioned; the island must never hold the service key.

Rejected: A browser-side call with an embedded key.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Live endpoint verification needs search-svc running.
