# sf-079 — Moved chrome outside .sf-shop so the gutter applies once, removed the footer max-width and auth phantom padding, forced request-fresh shell config, and unified Breadcrumbs/title with a single type scale

- Repo: `storefront-ui`
- Verified: 2026-11-26
- Commit(s): 0be6c24

## What

Moved chrome outside .sf-shop so the gutter applies once, removed the footer max-width and auth phantom padding, forced request-fresh shell config, and unified Breadcrumbs/title with a single type scale.

## Why

A 5-minute revalidation only shortened, not removed, cross-route drift; stale cached HTML even referenced a missing CSS hash. Rejected: shortening the window.

## Verification

Coordinator checked clean trees, author identity and four green gates per task:
lint 0 errors, typecheck clean, 1434 tests in 197 files, webpack build green.
Browser at 1536px and 375px confirmed one page gutter, byte-identical shell
across /, /products, /about, /blog, /privacy and /cart with cms-svc running,
a compact degraded face, a 70px collapsed filter rail with first product at
y=322, a 4-column compare table, shared cart rows and no /components route.

## Follow-ups

- Wordmark is Next.7 from real CMS navigation.shared.logo.wordmark; change it in CMS if a different brand is wanted.
