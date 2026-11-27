# sf-097 — Closed focus-visible/keyboard parity and reduced-motion gaps; restored shared empty card, compare breadcrumb/eyebrow and auth display font found by the visual harness

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): d87d3da, bf32f07

## What

Closed focus-visible/keyboard parity and reduced-motion gaps; restored shared empty card, compare breadcrumb/eyebrow and auth display font found by the visual harness.

## Why

A11y and empty-state contracts belong in shared CSS; per-component duplication would drift. Rejected: compare-only wrappers and local rings.

## Verification

Coordinator verified clean trees, author identity and gates. Final storefront:
251 files / 1694 tests, lint 0 errors, tsc and webpack green. Harness rerun:
0 PASS / 4 DIFF / 18 SKIP / 0 FAIL; compare improved from 40.85% to 35.23%
desktop and 41.37% to 37.06% mobile after the parity follow-up. Remaining
diffs are CMS/content/seeded-state differences, deliberately not faked.

## Follow-ups

- No runtime axe/screen-reader run; static and jsdom checks only.
- Remaining compare/signin diffs are CMS content and seeded-state differences.
