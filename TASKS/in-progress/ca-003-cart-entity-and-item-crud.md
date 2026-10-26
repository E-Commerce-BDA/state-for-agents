# ca-003 — Cart entity and item CRUD (in progress, claimed 2026-10-27)

## What

Implement the active-cart ensure path and the item operations the storefront
needs: add, update quantity, remove one, batch remove, clear, and read with
totals. Add idempotency and the one-event-per-mutation rule.

## How

- `src/cart/cart.repository.ts` — active cart by user/session; insert with
  `23505` retry; item reads/writes; ownership checks.
- `src/cart/cart.service.ts` — snapshots, totals, qty validation, clear.
- `src/cart/catalog.client.ts` — `CatalogClient` port +
  `FixtureCatalogClient` (v1) + `HttpCatalogClient` (later).
- `src/cart/idempotency.*` — Redis key → response, 24h TTL, body conflict.
- `src/cart/cart.controller.ts` — `GET /cart`, item POST/PATCH/DELETE,
  batch delete, clear.
- `src/events/event-bus.ts` — no-op adapter for `cart.updated` until Kafka
  is available.
- `test/cart.*` — guest/user ownership, totals, idempotency, one event,
  foreign item 404, Redis-down 503.

## Decisions

- Store product snapshots at add time — cart reads never join catalog.
  Rejected: live catalog lookup (couples services, breaks offline).
- Fail closed when Redis is unavailable for keyed mutations — a double-add
  is worse than a short 503. Rejected: best-effort dedupe.
- One `cart.updated` per mutation, after commit, fire-and-forget. Rejected:
  await the broker (latency + false failure).
- `qty = 0` is a removal, not an update. Rejected: allowing zero rows.

## Verification

Pending. Gate: unit + e2e green, `tsc --noEmit`, `oxlint`, `nest build`;
P99 cart read/removal targets from `3.Database-Schema.md` §6.
