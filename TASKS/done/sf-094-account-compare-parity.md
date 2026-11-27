# sf-094 — Account tabs are URL-driven, orders use shared rows, and compare uses a pure differences-only resolver and table

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): b60bb3d

## What

Account tabs are URL-driven, orders use shared rows, and compare uses a pure differences-only resolver and table.

## Why

URL is the tab source of truth; a useState mirror would drift. Rejected server checkbox for tab state.

## Verification

Coordinator verified clean tree, author identity and four gates after each
commit. Final storefront suite: 242 files / 1627 tests, lint 0 errors
(40 pre-existing warnings), tsc clean, webpack build green. Agent served
storefront.html and next dev locally; auth and styled 404 were browser-captured.

## Follow-ups

- Full visual parity requires live account/order/catalog services.
