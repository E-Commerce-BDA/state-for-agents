# cat-003 — Phase 4: Products & Multi-Variant PDP single-join queries (in-progress)

## What

Implement products listing with cursor pagination, multi-attribute filtering (category, brand, price range, status), sorting, single-join Product Detail Page (PDP) assembly using PostgreSQL `json_agg` / `jsonb_build_object`, active discount resolution, multi-variant, option, image, and discount CRUD management with `@Roles('admin')` RBAC.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2`.
- CLI-first scaffolding: Controllers and services in `src/products/`.
- Repository layer: Raw parameterized SQL queries in `products.repository.ts`.
- Single-Join PDP query: Assemble product, variants with option combinations (`pvov`), option sets (`product_options` + `product_option_values`), gallery images, and currently active scheduled discounts in a single database round-trip.
- Cursor pagination: Bounded opaque/id cursor (`WHERE (price, id) > ($cursorPrice, $cursorId)` or `WHERE (created_at, id) < ($cursorCreated, $cursorId)`).
- Admin management endpoints for variants, options, images, and discounts.
- Verification: Unit tests for services and controllers; comprehensive E2E test suite covering listing, filtering, PDP resolution, and admin mutations.

## Decisions

- Dual route prefix support `['catalog/products', 'products']` for reverse-proxy compatibility.
- Single-join query with PostgreSQL `json_agg` to eliminate N+1 queries on PDP.
- Soft-deletes for products (`deleted_at = now()`, `status = 'archived'`).

## Verification

Pending. Gate: unit + e2e green, `oxlint --type-aware`, `nest build`.
