# cat-005 — Phase 6: Hardening, security, and verification (done)

## What

Completed final hardening, security headers, Cache-Control policies (`public, max-age=60` on public catalog, `s-maxage=300, stale-while-revalidate=600` on navbar categories, `no-store` on internal/stock), request ID correlation, security regression tests, and full test suite verification for `catalog-svc`.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/4.API-Design.md §3.2 & §7`.
- Cache-Control policies:
  - Added dedicated `@Get('navbar')` in `CategoriesController` with `@Header('Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=600')`.
  - Added `@Header('Cache-Control', 'public, max-age=60')` to public categories, brands, and products GET endpoints.
  - Added `@Header('Cache-Control', 'no-store')` to internal service endpoints and stock mutations.
- Request correlation & Error envelope:
  - Ensured `HttpExceptionFilter` echoes `x-request-id` in response headers and standardizes error envelope `{ error: { code, message, details? }, requestId, timestamp }`.
- Security & Prototype pollution:
  - Strict validation pipe enforcement (`whitelist: true, transform: true`).
  - Comprehensive security E2E test suite in `test/security.e2e-spec.ts` verifying prototype pollution stripping, SQL injection safety in search queries, unauthorized header tampering, error envelope consistency, and request correlation.
- Verification:
  - All 16 unit test files passing (82/82 tests).
  - All 8 e2e test files passing (67/67 tests).
  - `oxlint --type-aware` with 0 errors and 0 warnings on 87 files.
  - `nest build` clean compilation (exit code 0).

## Decisions

- Explicit HTTP headers via NestJS `@Header` decorator for predictable caching proxy / CDN behavior.
- Error envelope standardization across all status codes and request ID response header echo.

## Verification

- Vitest unit suite: 82/82 passed across 16 test files.
- Vitest e2e suite: 67/67 passed across 8 test files (`security.e2e-spec.ts`, `internal.e2e-spec.ts`, `inventory.e2e-spec.ts`, `products.e2e-spec.ts`, `categories.e2e-spec.ts`, `brands.e2e-spec.ts`, `health.e2e-spec.ts`, `schema.e2e-spec.ts`).
- Oxlint: 0 warnings, 0 errors across 87 files.
- Nest build: clean compilation (exit code 0).
