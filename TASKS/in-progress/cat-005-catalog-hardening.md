# cat-005 — Phase 6: Hardening, security, and verification (in-progress)

## What

Complete final hardening, security headers, Cache-Control policies (`public, max-age=60` on public catalog, `no-store` on internal/stock), security regression tests, and full test suite verification for `catalog-svc`.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/4.API-Design.md §3.2 & §7`.
- Cache-Control policies:
  - Add `@Header('Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=600')` to categories navbar.
  - Add `@Header('Cache-Control', 'public, max-age=60')` to public categories, brands, and products GET endpoints.
  - Add `@Header('Cache-Control', 'no-store')` to internal endpoints and stock mutations.
- Security & Prototype pollution:
  - Ensure strict validation pipe enforcement (`whitelist: true`).
  - Security tests verifying forbidden non-whitelisted properties, SQL injection safety in search queries and filters, unauthorized header tampering, and error envelope consistency.
- Verification:
  - All unit test files passing.
  - All e2e test files passing.
  - `oxlint --type-aware` with 0 errors and 0 warnings.
  - `nest build` clean compilation.

## Decisions

- Explicit HTTP headers via NestJS `@Header` decorator for predictable caching proxy / CDN behavior.
- Error envelope standardization across all status codes.

## Verification

Pending. Gate: unit + e2e green, `oxlint --type-aware`, `nest build`.
