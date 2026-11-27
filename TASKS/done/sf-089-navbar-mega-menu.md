# sf-089 — Wired CMS 2.2.0 mega-menu groups through navSettings/resolveNav/NavbarMount/NavLinks/MegaMenu with current-link marking and prototype hover language

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 957b64e

## What

Wired CMS 2.2.0 mega-menu groups through navSettings/resolveNav/NavbarMount/NavLinks/MegaMenu with current-link marking and prototype hover language.

## Why

One shell config and one nav model across all routes; a local duplicate group shape would drift from the contract. Rejected: page-local nav overrides.

## Verification

Coordinator verified clean tree, author identity and four gates: lint 0 errors,
tsc clean, 1565 tests in 220 files, webpack build with 54/54 static pages.
Browser at 1536x900 and 375x812 confirmed sticky 64px navbar, 8px radii,
hover wash/border, dark footer, 0.45 scrim, right cart drawer with 0.24s
transition reduced to 0s, focus-trapped search dialogs, and bottom-right toast
stack.

## Follow-ups

- Live CMS has no groups configured, so the drop was verified by contract/CSSOM probe, not a populated live menu.
