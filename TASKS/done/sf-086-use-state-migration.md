# sf-086 — Migrated 13 useState-heavy islands to reducer machines; useRef/useEffect now own only timers, abort and focus side effects

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 24dbedc

## What

Migrated 13 useState-heavy islands to reducer machines; useRef/useEffect now own only timers, abort and focus side effects.

## Why

Duplicate local flags caused undefined states; one reducer per island is the single source of truth. Rejected: adding more booleans.

## Verification

Coordinator verified clean trees, author identity and four gates. Final Wave 1
storefront gate: lint 0 errors (40 advisory), tsc clean, 215 files / 1537 tests,
webpack build green. Docs check: 64 links resolve, diff clean.

## Follow-ups

- Browser visual parity deferred to later waves.
