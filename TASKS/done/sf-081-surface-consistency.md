# sf-081 — Mapped search results to ProductCard, forwarded theme/columns to every grid, collapsed the filter rail, unified cart/order rows and account pricing, replaced the compare grid with a table, and deleted the temporary /components route

- Repo: `storefront-ui`
- Verified: 2026-11-26
- Commit(s): cc011ce

## What

Mapped search results to ProductCard, forwarded theme/columns to every grid, collapsed the filter rail, unified cart/order rows and account pricing, replaced the compare grid with a table, and deleted the temporary /components route.

## Why

The same product rendered differently across surfaces and the filter rail buried products below the fold. Rejected: a taller scroll-only rail.

## Verification

Coordinator checked clean trees, author identity and four green gates per task:
lint 0 errors, typecheck clean, 1434 tests in 197 files, webpack build green.
Browser at 1536px and 375px confirmed one page gutter, byte-identical shell
across /, /products, /about, /blog, /privacy and /cart with cms-svc running,
a compact degraded face, a 70px collapsed filter rail with first product at
y=322, a 4-column compare table, shared cart rows and no /components route.

## Follow-ups

- Live product images are empty in seed data, so image-filled cells were verified in component tests only.
