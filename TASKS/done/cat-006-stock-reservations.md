# cat-006 — catalog-svc: idempotent stock reservations

## What

Stock reservation becomes a persisted catalog resource instead of an anonymous
decrement. `POST /catalog/internal/stock/reserve` now requires a client-supplied
`reservationId`, writes a `catalog.stock_reservations` row (`held`), and replays
the stored result when the same id arrives again. `release` takes only the
reservation id and restores exactly the stored items once; `commit` marks a held
reservation consumed by a real order; a cron sweep expires stale holds. This is
what makes `order-svc` checkout both possible (the DTO now matches) and safe
(the old release path could inflate stock on replay).

## How

- `db/003-stock-reservations.sql` — new table, partial indexes, `stock_movements.reservation_id`.
- `src/stock/` — `stock.types.ts`, `dto/{reserve,release,commit}-stock.dto.ts`, `stock-reservations.repository.ts`, `stock-reservations.service.ts`, `stock-reservations.scheduler.ts`, `stock.module.ts`.
- `src/internal/internal.controller.ts` — reserve/release delegate to the new service; adds `stock/commit` and `stock/reservations/:id` (`ParseUUIDPipe` + `Cache-Control: no-store`).
- `src/inventory/` — reserve/release removed from service and repository (≈200 lines); their DTOs deleted; `CatalogProductSnapshot` gains `sku` (both UNION branches).
- `@nestjs/schedule@12.0.2` + `ScheduleModule.forRoot()`; Joi key `STOCK_RESERVATION_TTL_SECONDS` (min 60, default 900).
- Tests: `test/internal.e2e-spec.ts`, `test/schema.e2e-spec.ts`, `src/stock/stock-reservations.service.spec.ts`, plus the updated `inventory`/`internal` unit specs.

## Decisions (+ one rejected alternative each)

- Client-supplied `reservationId` as the primary key, with `INSERT … ON CONFLICT DO NOTHING` as the idempotency gate. Reason: the second replay blocks on the PK index entry until the first commits, so serialization is free — no advisory lock, no Redis. Rejected: server-generated id plus a lookup table on `(orderId, items-hash)`, which cannot distinguish a retry from a genuine second order.
- `release`/`commit` take only `reservationId`. Reason: release restores the stored items, so a caller can no longer dictate quantities and inflate stock. Rejected: keep `items` in the release DTO for backward compatibility — that preserves the bug being fixed.
- Hold decrements stock immediately; `commit` does not touch stock. Reason: no overselling inside the payment window and no double decrement. Rejected: decrement at commit, which needs an availability recheck and a second failure mode.
- `release` of a `committed` hold is `409 RESERVATION_CLOSED`, while a replayed release of a `released`/`expired` hold is an idempotent no-op. Reason: retrying a release must be safe, but a committed hold's stock was legitimately sold — restoring it would oversell. Rejected: uniform "terminal ⇒ no-op", which silently hides a checkout that committed and then tried to compensate.
- One reservation per order for the lifetime of the order: `idx_stock_reservations_order` is `UNIQUE (order_id) WHERE order_id IS NOT NULL`, not `WHERE status = 'held'`. Reason: a released hold's order id is never reused (order-svc mints a new order id per attempt), so reusing it would only mask a duplicate-order bug. Rejected: status-scoped uniqueness, which allows two rows to claim the same order.
- Expiry sweep on `@nestjs/schedule` `@Cron`, skipping when `NODE_ENV === 'test'`. Rejected: opportunistic expiry inside `reserve` only, which never reclaims holds for products that are not ordered again.
- e2e fixtures created by `internal.e2e-spec.ts` are archived in `afterAll`. Reason: e2e files share one database and run sequentially, and ~10 extra active products pushed the seeded products off page 1 of the public listing (which `products.e2e-spec.ts` asserts). Those two assertions now also request `limit=100`.

## Verification

All commands run from `catalog-svc` on 2026-10-29:

| Gate | Result |
|---|---|
| `pnpm lint` (oxlint --type-aware) | 100 files, 0 warnings, 0 errors |
| `pnpm test` | 18 files / 89 tests passed (incl. 7 new `stock-reservations.service` cases) |
| `pnpm test:e2e` | 8 files / 75 tests passed (16 schema + 10 internal) |
| `pnpm build` | `nest build` clean (includes `tsc --noEmit`: 0 errors) |
| migration | `db/003-stock-reservations.sql` applied to `ecom-pg` (`CREATE TABLE`, 3 indexes, `ALTER TABLE … ADD COLUMN`) |

Contract behaviour proven by `test/internal.e2e-spec.ts`:
reserve replay decrements once and writes exactly one `sale` movement; an
unsatisfiable hold rolls back leaving stock untouched (`INSUFFICIENT_STOCK`);
release restores the stored items and a replay returns `items: []`; release
after commit is `409 RESERVATION_CLOSED`; the sweep expires a stale hold,
restores its stock and flips the status to `expired`; the legacy `{qty}` body is
rejected 400 naming `quantity`; the literal order-svc body is accepted.

Cross-service proof lives in `ord-007` (a live checkout decremented stock
10 → 8 in this schema and stored the matching `stock_reservations` row).

### Live replay (service on `:4020`, 2026-10-29)

| Call | Observed |
|---|---|
| `POST stock/reserve` (same `reservationId`, ×2) | 201, 201; stock 10 → 8; movements `[{-2, sale, 8}]` |
| `POST stock/release` (×2) | 201 with restored items, then 201 with `items: []`; stock back to 10 |
| `POST stock/commit` then `stock/release` | 201 committed; 409 `RESERVATION_CLOSED` |

The replayed reserve body carries the same values but not the same key order
(`jsonb` normalises object keys), so the promise is "same result", not
"same bytes" — clients must read fields, not compare raw JSON.

## Follow-ups

- `ec-002`: move the reserve/release/commit request+response shapes into `@ecom/contracts` so both services compile against one type.
- `cat-009`: consume `order.created` and call `commit` (today the hold expires after 900s, restoring stock for an order that already exists).
