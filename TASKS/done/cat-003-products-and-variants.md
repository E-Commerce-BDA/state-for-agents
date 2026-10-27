# cat-003 — Phase 4: Products & Multi-Variant PDP single-join queries (done)

## What

Implemented products listing with cursor pagination, multi-attribute filtering (category, brand, price range, status), sorting, single-join Product Detail Page (PDP) assembly using PostgreSQL `json_agg` / `json_build_object`, active discount resolution, multi-variant, option, image, and discount CRUD management with `@Roles('admin')` RBAC.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2`.
- CLI-first scaffolding: Controllers and services in `src/products/`.
- Repository layer: Raw parameterized SQL queries in `products.repository.ts`.
- Single-Join PDP query: Assemble product, category, brand, gallery images (`json_agg`), options with nested values (`json_agg`), variants with joined option values (`pvov`), and currently active scheduled discounts in a single database round-trip without N+1 overhead.
- Cursor pagination: Bounded opaque/id cursor (`WHERE (price, id) > ($cursorPrice, $cursorId)` or `WHERE (created_at, id) < ($cursorCreated, $cursorId)`).
- Admin management endpoints for variants (`VariantsController`), images (`ImagesController`), and discounts (`DiscountsController`).
- Verification: Unit tests for services and controllers (11 tests); comprehensive E2E test suite covering listing, filtering, PDP resolution, active discounts, variants, images, and admin mutations (17 tests).

## Decisions

- Support dual route prefix `['catalog/products', 'products']` for reverse-proxy compatibility.
- Single-join query with PostgreSQL `json_agg` / `json_build_object` to eliminate N+1 queries on PDP.
- Soft-deletes for products (`deleted_at = now()`, `status = 'archived'`).
- Effective price computation dynamically accounting for percentage or fixed active discounts.

## Verification

- Vitest unit suite: 61/61 passed across 12 test files (`products.service.spec.ts`, `products.controller.spec.ts`, etc.).
- Vitest e2e suite: 55/55 passed across 5 test files (`products.e2e-spec.ts`, `categories.e2e-spec.ts`, `brands.e2e-spec.ts`, `health.e2e-spec.ts`, `schema.e2e-spec.ts`).
- Oxlint: 0 warnings, 0 errors across 72 files.
- Nest build: clean compilation (exit code 0).
