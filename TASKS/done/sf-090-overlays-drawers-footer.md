# sf-090 — Unified search overlays, drawers, compare tray, toast stack, footer and scrim under shared state faces, tokens and .sf-drawer motion

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 2d69d92

## What

Unified search overlays, drawers, compare tray, toast stack, footer and scrim under shared state faces, tokens and .sf-drawer motion.

## Why

One visual language for all overlays; hand-rolled faces caused inconsistency. Rejected: per-overlay implementations.

## Verification

Coordinator verified clean tree, author identity and four gates: lint 0 errors,
tsc clean, 1565 tests in 220 files, webpack build with 54/54 static pages.
Browser at 1536x900 and 375x812 confirmed sticky 64px navbar, 8px radii,
hover wash/border, dark footer, 0.45 scrim, right cart drawer with 0.24s
transition reduced to 0s, focus-trapped search dialogs, and bottom-right toast
stack.

## Follow-ups

- Live quick-add toast not exercised because upstream services refused connections during the run.
