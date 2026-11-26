# sf-078 — Defined one :root token set for surfaces, navy, scrim, radii, z-index, type scale and canonical error/success colors; removed the duplicate .sf-pill base rule and the three verified opacity faces; themed the SearchSheet backdrop

- Repo: `storefront-ui`
- Verified: 2026-11-26
- Commit(s): d1ad18f

## What

Defined one :root token set for surfaces, navy, scrim, radii, z-index, type scale and canonical error/success colors; removed the duplicate .sf-pill base rule and the three verified opacity faces; themed the SearchSheet backdrop.

## Why

Undefined variables and competing values were the main cause of inconsistent paint. Rejected: more per-component fallbacks.

## Verification

Coordinator checked clean trees, author identity and four green gates per task:
lint 0 errors, typecheck clean, 1434 tests in 197 files, webpack build green.
Browser at 1536px and 375px confirmed one page gutter, byte-identical shell
across /, /products, /about, /blog, /privacy and /cart with cms-svc running,
a compact degraded face, a 70px collapsed filter rail with first product at
y=322, a 4-column compare table, shared cart rows and no /components route.

## Follow-ups

- Local axe scan not run; jsx-a11y lint and contrast contract tests pass.
