# sf-092 — Products listing uses one ListingShell for drawer/grid machines; PDP tabs, gallery, variants and sections reuse existing components

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 0b1b48b

## What

Products listing uses one ListingShell for drawer/grid machines; PDP tabs, gallery, variants and sections reuse existing components.

## Why

Sibling islands cannot share inline grid vars honestly; one shell owns the state. Rejected CSS-only mode sharing.

## Verification

Coordinator verified clean tree, author identity and four gates after each
commit. Final storefront suite: 242 files / 1627 tests, lint 0 errors
(40 pre-existing warnings), tsc clean, webpack build green. Agent served
storefront.html and next dev locally; auth and styled 404 were browser-captured.

## Follow-ups

- Full visual parity requires live catalog/CMS.
