# doc-010 — Finalized component indexes, shipped/deferred statuses, preview draft/CSP amendments and testing-doc ledger for the rebuilt storefront

- Repo: `Documentation`
- Verified: 2026-11-27
- Commit(s): c8706c2

## What

Finalized component indexes, shipped/deferred statuses, preview draft/CSP amendments and testing-doc ledger for the rebuilt storefront.

## Why

Docs must match shipped code; stale planned rows would mislead. Rejected: leaving doc-009 planning language.

## Verification

Coordinator verified clean trees, author identity and gates. Final storefront:
251 files / 1694 tests, lint 0 errors, tsc and webpack green. Harness rerun:
0 PASS / 4 DIFF / 18 SKIP / 0 FAIL; compare improved from 40.85% to 35.23%
desktop and 41.37% to 37.06% mobile after the parity follow-up. Remaining
diffs are CMS/content/seeded-state differences, deliberately not faked.

## Follow-ups

- Owner docs form-controls.md, navigation.md, feedback.md and product grid-mode remain deferred and are named as such.
