# tst-004 — Opt-in visual parity harness serves storefront.html and the Next storefront, captures 11 routes at two viewports, diffs with pixelmatch/pngjs and reports SKIP for service/data-dependent routes

- Repo: `ecom-infra`
- Verified: 2026-11-27
- Commit(s): 26e8f64

## What

Opt-in visual parity harness serves storefront.html and the Next storefront, captures 11 routes at two viewports, diffs with pixelmatch/pngjs and reports SKIP for service/data-dependent routes.

## Why

Pixel parity must be measured, not eyeballed; blocking CI on unavailable services would be wrong. Rejected: always-on CI job.

## Verification

Coordinator verified clean trees, author identity and gates. Final storefront:
251 files / 1694 tests, lint 0 errors, tsc and webpack green. Harness rerun:
0 PASS / 4 DIFF / 18 SKIP / 0 FAIL; compare improved from 40.85% to 35.23%
desktop and 41.37% to 37.06% mobile after the parity follow-up. Remaining
diffs are CMS/content/seeded-state differences, deliberately not faked.

## Follow-ups

- No approved reference baseline; DIFF is a report, not a gate.
- Six routes need live services and two need an access cookie.
