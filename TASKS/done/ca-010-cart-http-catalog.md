# ca-010 — cart-svc: price add-to-cart from catalog-svc over HTTP (done, 2026-10-31)

## What

`POST /cart/items` snapshotted its price from `FixtureCatalogClient` — a hard-coded table of
demo products. Every cart therefore stored a fake price and a fake name, and `order-svc` would
re-price checkout from a snapshot that never matched the catalog. This task wires the real
`HttpCatalogClient`, moves the fixture to test-only, and makes catalog failure **fail closed**:
a cart line is never written with a price the service invented.

## How

- `src/cart/catalog.client.ts` — the port only now: `CatalogClient`, `CatalogSnapshot`, the
  `CATALOG_CLIENT` token, and the one error class every adapter raises
  (`CatalogUnavailableError`). 61 lines became 3 exports.
- `src/cart/http-catalog.client.ts` (new) — one batch call per add:
  `GET {CATALOG_SVC_URL}/api/v1/catalog/internal/products?ids=<variantId ?? productId>` with
  `x-service-key`, `AbortSignal.timeout(1500)` and a zod shape check on the response row.
  Snapshot price = `effectivePrice ?? unitPrice`. Two failure classes, deliberately different:
  transport/shape → `503 CATALOG_UNAVAILABLE`; an empty or mismatched `data` array → `null`,
  which `cart.service.ts` maps to `422 CART_PRODUCT_UNAVAILABLE`.
- `CATALOG_FETCH` — an optional provider defaulting to the global `fetch`, so
  `http-catalog.client.spec.ts` never opens a socket.
- `src/cart/catalog.fixture.ts` — `FixtureCatalogClient` moved here, test-only, documented as
  such. Every e2e suite overrides `CATALOG_CLIENT` with it (8 suites touched), so the suite needs
  neither catalog-svc nor a network.
- `src/cart/cart.module.ts` — the production binding is `HttpCatalogClient`; `CATALOG_SVC_URL`
  is validated by the Joi schema in `app.module.ts` and recorded in `.env.example`.
- `test/catalog-failure.e2e-spec.ts` (new) — the fail-closed proof, against the real cart stack.

## Decisions

1. **Fail closed, always.** No fallback price, no "snapshot from the request body", no cached
   catalog row. Rejected: accept a client-supplied price when catalog is down — that is a
   price-tampering hole with a friendly name.
2. **Snapshot the payable price (`effectivePrice ?? unitPrice`).** `order-svc` re-prices checkout
   from the same field, so any other choice makes the cart and the order disagree about money.
   Rejected: snapshot the list `unitPrice` and let the order apply the discount — that makes the
   cart total a lie the shopper only discovers at checkout.
3. **One batch call, keyed by variant when the line has one.** A variant price can differ from its
   product's, so the product id alone is the wrong key. Rejected: per-item HTTP (N+1 latency on a
   multi-line cart) and product-id-only lookup (wrong price for variants).
4. **The upstream reason is logged, never returned.** The 503 body carries the code and nothing
   else; the upstream status, URL and parse error go to the structured log. Rejected: return
   catalog's error text — it leaks internal topology to the buyer.
5. **The fixture stays, but only in tests.** Deleting it would force every e2e suite onto the
   network and make the cart suite depend on catalog-svc being up. Rejected: delete the fixture
   and wire e2e to a live catalog — the cart suite would then fail for reasons that are not cart.
6. **The adapter is chosen at module wiring, not by env flag.** One provider, no
   `if (NODE_ENV === 'test')` inside the client. Rejected: a runtime flag, which makes production
   and test exercise different code paths.

## Verification

| Check | Result |
|---|---|
| `cart-svc` `pnpm test` | 103 passed (15 files) |
| `cart-svc` `http-catalog.client.spec.ts` | 12 cases: ids query by variant then product, `effectivePrice` beats `unitPrice`, `x-service-key` sent, abort signal present, catalog-only fields dropped, `available:false` preserved, empty/mismatched `data` → `null`, 5xx / abort / non-JSON / shape-invalid → `503 CATALOG_UNAVAILABLE` |
| `cart-svc` `test/catalog-failure.e2e-spec.ts` | `503 CATALOG_UNAVAILABLE` with no upstream detail in the body, and no cart, no line and no `cart.outbox` row written; warms Redis first because `enableOfflineQueue: false` would otherwise answer 503 for the wrong reason |
| `cart-svc` `pnpm test:e2e` | 99 passed, 1 skipped (12 files; the live Kafka spec is skipped by default) |
| `cart-svc` `pnpm lint` | 0 warnings, 0 errors |
| `cart-svc` `tsc --noEmit --incremental false` | exit 0 |
| `cart-svc` `nest build` | clean |
| commit | `cart-svc` `cb305e7` |

## Open

- The e2e run above is the 2026-10-31 run with the compose stack up. The commit-day gate re-ran
  lint, unit, `tsc` and build; e2e was not re-run after the final doc edit (no code changed).
- `CATALOG_SVC_URL` has no retry and no circuit breaker. A slow catalog is a slow add-to-cart;
  the 1.5 s abort caps it, but there is no "skip the call, serve a cached snapshot" mode.
- `CATALOG_UNAVAILABLE` has no metric yet — recorded as observability debt in
  `Documentation/10.Observability.md`.
- The fixture table is now the only place a demo product exists in cart-svc; do not let it grow
  into a second catalog.
