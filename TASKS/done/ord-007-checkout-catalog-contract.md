# ord-007 — order-svc: checkout/catalog stock contract + persisted reservationId

## What

`order-svc` now speaks the catalog's real reservation contract and stores the
link. Before: it sent `{reservationId, items:[{…, qty}]}`, catalog's
`ValidationPipe({whitelist:true})` stripped `qty`, `quantity` was missing, and
every checkout died on 400 — hidden by a mocked `CatalogClient` in the e2e suite.
The reservation id also lived only in memory, so a crash lost the ability to
release or commit. After: `quantity` is sent, the real response is parsed, the id
is persisted on `orders.stock_reservation_id`, and it is carried in the
`order.created` outbox payload.

## How

- `db/003-orders-stock-reservation.sql` — `orders.stock_reservation_id` + partial index.
- `src/clients/catalog.client.ts` — real request/response types, discriminated `ok/failure` result, 409/400/5xx taxonomy, 3s `AbortSignal.timeout` on every call, snapshot map keyed by `variantId ?? productId`, `commitStock()` added for `cat-009`.
- `src/checkout/checkout.service.ts` — item mapping (`quantity: i.qty`), failure mapping (409/502/503), snapshot key, release by id (three call sites), `stock_reservation_id` column, `reservationId` in the outbox payload.
- `src/db/rows.ts` — `OrderRow.stock_reservation_id`.
- Tests: `test/checkout.e2e-spec.ts` (applies every `db/*.sql` in filename order, contract-faithful fake, variant-pricing case, catalog-409 case, live gated case), `src/checkout/checkout.service.spec.ts`.

## Decisions (+ one rejected alternative each)

- Translate `qty → quantity` inside `CatalogClient`, not in `CheckoutDto`. Reason: `qty` is the public checkout field in `4.API-Design`; the internal wire name is the client's business. Rejected: rename the public DTO field, which breaks the documented storefront contract for no gain.
- Discriminated result (`{ok: false, failure}`) instead of `success: boolean`. Reason: the caller must distinguish "out of stock" (409, user's fault) from "catalog down" (503, our fault); the old boolean collapsed both into 409. Rejected: keep the boolean and re-inspect a message string.
- `releaseStock` treats 404/409 as success. Reason: the desired end state is "this hold is gone", and compensation must never fail the checkout it is cleaning up. Rejected: propagate the error, which turns a successful cleanup into a 500.
- Snapshot lookups keyed by `variantId ?? productId`, requested with the same key. Reason: the catalog endpoint resolves ids that are either, so a variant line previously read back the product-level price and SKU. Rejected: add a second catalog endpoint for variant snapshots (a new contract surface for a client-side fix).
- Replace the loose mock with a contract-faithful fake that rejects `qty` and requires a UUID reservation id. Reason: the mock is what let this bug ship; a fake that validates the body would have caught it. Rejected: no mock at all, which would make the suite depend on a running catalog for every case.
- The DB transaction does not call `commit` yet. Reason: commit is triggered by `order.created` in `cat-009`; adding a synchronous cross-service call inside the transaction would either lose stock (commit before `COMMIT`) or oversell (commit after, if the expiry sweep fires first). Rejected: commit inline after the order `COMMIT` — an unreachable catalog would then leave a paid order whose hold expires.

## Verification

All commands run from `order-svc` on 2026-10-29:

| Gate | Result |
|---|---|
| `pnpm lint` (oxlint --type-aware) | 65 files, 0 warnings, 0 errors |
| `pnpm test` | 5 files / 47 tests passed |
| `pnpm test:e2e` | 6 files / 62 tests passed, 1 skipped (live catalog case) |
| `pnpm build` | `nest build` clean (`tsc --noEmit`: 0 errors) |
| migration | `db/003-orders-stock-reservation.sql` applied by the e2e bootstrap |

### Live acceptance (both services running, Postgres on 5433)

Seeded a catalog product (stock 10, price 40), then:

```
POST http://localhost:4040/api/v1/checkout   → 201 (was 400 before this task)
{"orderId":"f5367d16-…","totals":{"subtotal":80,"shipping":5,"grandTotal":85},
 "items":[{"productName":"Live Contract Item","sku":"SKU-LIVE-s3leqg","unitPrice":40,"qty":2}]}
```

Verified afterwards in Postgres:

| Check | Observed |
|---|---|
| `orders.stock_reservation_id` | `8f6978ca-e629-461a-8396-74f112844930` (set) |
| `catalog.stock_reservations` | same id, `status = held`, `items` = `[{quantity: 2, productId, variantId: null, remainingStock: 8}]` |
| `catalog.products.stock` | 8 (was 10 — decremented exactly once) |
| `catalog.stock_movements` | one row: `reservation_id` set, `qty_change = -2`, `reason = sale`, `qty_after = 8` |
| `order.outbox.payload->>'reservationId'` | same id |

The real SKU and the real price in the response prove the snapshot path and the
`sku` addition work across services (previously `SKU-` + 8 hex and a `$50`
fallback).

## Follow-ups

- `cat-009`: commit the hold from `order.created`; until then a completed order's hold is released by the 900s expiry sweep.
- `ord-009` (unchanged, still open): `$50` snapshot fallback, hardcoded shipping, `tax = 0`, capture-before-`BEGIN`, missing refund on rollback, `#2026-\d{6}` collision.
- `ec-002`: the `order.created` payload now carries `reservationId`, which is not yet in the contracts package.
