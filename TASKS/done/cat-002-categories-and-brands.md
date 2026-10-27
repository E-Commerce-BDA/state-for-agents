# cat-002 — Phase 3: Categories and brands subsystem with navbar query optimization (done)

## What

Implemented categories and brands domain logic, repository queries with navbar partial index optimization (`idx_categories_navbar`), self-referencing category tree builder, slug lookups, admin CRUD endpoints with `@Roles('admin')` guard, shared error envelope, and unit/e2e test suites.

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2`.
- CLI-first scaffolding: Controllers and services in `src/categories/` and `src/brands/`.
- Repository layer: Pure parameterized SQL via PostgreSQL `Pool` in `categories.repository.ts` and `brands.repository.ts`.
- Navbar optimization: `findNavbarCategories()` queries using `WHERE is_active = true AND show_in_navbar = true AND deleted_at IS NULL ORDER BY sort_order ASC, name ASC` directly scanning `idx_categories_navbar`.
- Tree builder: In-memory O(n) category tree construction for `GET /api/v1/catalog/categories?tree=true` & `/api/v1/catalog/categories/tree`.
- Admin CRUD: Gated by `JwtAuthGuard` and `RolesGuard` (`@Roles('admin')`) for create, update, soft-delete.
- Verification: Unit tests for services, controllers, and guards (50 tests); e2e suites for public reads and admin mutations (38 tests).

## Decisions

- Support dual routes `['catalog/categories', 'categories']` and `['catalog/brands', 'brands']` for reverse-proxy compatibility.
- Soft-delete strategy: update `deleted_at = now()`, `is_active = false` rather than physical row deletion.
- Shared error envelope & request correlation matching platform standard.

## Verification

- Vitest unit suite: 50/50 passed across 10 test files.
- Vitest e2e suite: 38/38 passed across 4 test files (`categories.e2e-spec.ts`, `brands.e2e-spec.ts`, `health.e2e-spec.ts`, `schema.e2e-spec.ts`).
- Oxlint: 0 warnings, 0 errors across 55 files.
- Nest build: clean compilation (exit code 0).
