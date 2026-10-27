# cat-004 — Phase 5: Stock ledger & internal service-to-service endpoints for cart-svc and order-svc (in-progress)

## What

Implement stock ledger management, stock movements audit trail, atomic stock reservation with row locks (`SELECT ... FOR UPDATE`), and internal service-to-service endpoints (`GET /internal/products?ids=` for `cart-svc` snapshot hydration, `GET /internal/stock`, `POST /internal/stock/reserve`, and `POST /internal/stock/release` for `order-svc` checkout) protected by `ServiceKeyGuard` (`x-service-key`).

## How

- Docs-first: `Documentation/services/catalog.md`, `Documentation/3.Database-Schema.md §3.2`, `Documentation/4.API-Design.md §3.2 & §7`.
- Internal Auth: `ServiceKeyGuard` checking `x-service-key` against `INTERNAL_SERVICE_KEY` environment variable.
- Inventory Repository & Service:
  - Admin stock adjustment: `POST /api/v1/catalog/products/:id/stock` with `{ delta, reason }`, recording balance change and inserting into `catalog.stock_movements`.
  - Stock movements query: `GET /api/v1/catalog/products/:id/stock-movements` with cursor pagination.
  - Stock availability check: `GET /internal/stock?productId=&variantId=` returning `{ productId, variantId, stock, available }`.
  - Atomic stock reservation: `POST /internal/stock/reserve` with `{ items: [{ productId, variantId?, quantity }] }`, locking rows with `SELECT ... FOR UPDATE`, verifying `stock >= quantity`, decrementing stock balance, recording movement with `reason = 'sale'`, and returning reservation confirmation. If stock is insufficient, rolls back and returns 409 `INSUFFICIENT_STOCK`.
  - Reservation release (compensation): `POST /internal/stock/release` with `{ items: [{ productId, variantId?, quantity }] }` restoring stock balance with `reason = 'cancel'`.
  - Batch product snapshot lookup: `GET /internal/products?ids=` returning `{ data: CatalogProductSnapshot[] }` formatted with `id, name, slug, price, effectivePrice, imageUrl, variantLabel, available` for `cart-svc` hydration.
- Dual route prefix support `['catalog/inventory', 'inventory']` and `['catalog/internal', 'internal']`.
- Verification: Unit tests for inventory and internal services/guards; comprehensive E2E test suites for internal endpoints, atomic reservations, and concurrency safety.

## Decisions

- Internal service endpoints guarded by `x-service-key` header.
- Atomic stock reservations execute inside a single PostgreSQL transaction with row-level locks (`SELECT ... FOR UPDATE`) to prevent race conditions and overselling.
- Stock movements ledger records every stock delta with reason classification and balance snapshot (`qty_after`).

## Verification

Pending. Gate: unit + e2e green, `oxlint --type-aware`, `nest build`.
