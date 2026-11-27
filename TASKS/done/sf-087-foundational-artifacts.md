# sf-087 — Added SegmentedToggle, Menu, FilterDrawer, ShopToolbar and GridModeToggle with model/CSS/component/doc/barrel/trio artifacts

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): e0a0d95

## What

Added SegmentedToggle, Menu, FilterDrawer, ShopToolbar and GridModeToggle with model/CSS/component/doc/barrel/trio artifacts.

## Why

Prototype pieces need durable five-artifact homes rather than page-local markup. Rejected: reusing semantically wrong primitives.

## Verification

Coordinator verified clean trees, author identity and four gates. Final Wave 1
storefront gate: lint 0 errors (40 advisory), tsc clean, 215 files / 1537 tests,
webpack build green. Docs check: 64 links resolve, diff clean.

## Follow-ups

- New primitives not yet wired into product pages; Wave 2/3 integrates them.
