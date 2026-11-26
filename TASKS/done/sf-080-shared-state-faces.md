# sf-080 — Added LoadingState, ErrorState and DegradedState artifacts with model/CSS/docs/tests, converted 15 faces, added 9 route boundaries and wired the seven reducers left unused by sf-074

- Repo: `storefront-ui`
- Verified: 2026-11-26
- Commit(s): 8063385

## What

Added LoadingState, ErrorState and DegradedState artifacts with model/CSS/docs/tests, converted 15 faces, added 9 route boundaries and wired the seven reducers left unused by sf-074.

## Why

Eight hand-rolled faces made identical failures look different, and machine-tested states never rendered. Rejected: another generic toast.

## Verification

Coordinator checked clean trees, author identity and four green gates per task:
lint 0 errors, typecheck clean, 1434 tests in 197 files, webpack build green.
Browser at 1536px and 375px confirmed one page gutter, byte-identical shell
across /, /products, /about, /blog, /privacy and /cart with cms-svc running,
a compact degraded face, a 70px collapsed filter rail with first product at
y=322, a 4-column compare table, shared cart rows and no /components route.

## Follow-ups

- None.
