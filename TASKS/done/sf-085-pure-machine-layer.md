# sf-085 — Ported prototype state machines into domain-local pure reducers for shop filters/grid, cart view, auth forms, sections/carousel, account tabs, quick view, search overlay and PDP tabs

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): aa8eb53

## What

Ported prototype state machines into domain-local pure reducers for shop filters/grid, cart view, auth forms, sections/carousel, account tabs, quick view, search overlay and PDP tabs.

## Why

Explicit event unions reject wrong transitions at compile time; a generic factory or XState would add abstraction without enforcing domain invariants. Rejected: generic factory.

## Verification

Coordinator verified clean trees, author identity and four gates. Final Wave 1
storefront gate: lint 0 errors (40 advisory), tsc clean, 215 files / 1537 tests,
webpack build green. Docs check: 64 links resolve, diff clean.

## Follow-ups

- No generic machine factory; no XState.
