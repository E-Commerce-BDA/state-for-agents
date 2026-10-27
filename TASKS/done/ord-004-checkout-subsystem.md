# Task: ord-004 — Checkout & Idempotent Order Placement Subsystem for order-svc

## Summary
- Implemented strict DTOs for checkout:
  - `CheckoutItemDto`: strict non-optional `productId` and `qty`, optional `variantId`.
  - `AddressDto`: strict non-optional `line1`, `city`, `postalCode`, `country (2 chars)`, optional `line2`, `state`.
  - `PaymentRequestDto`: strict `provider ('mock' | 'stripe' | 'paypal')`.
  - `CheckoutDto`: validated nested items, addresses, payment, optional `discountCode` and `notes`.
- Implemented `CatalogClient`:
  - `reserveStock`: calls `POST /catalog/internal/stock/reserve` with `x-service-key`.
  - `releaseStock`: compensation endpoint calling `POST /catalog/internal/stock/release`.
  - `getProductSnapshots`: calls `GET /catalog/internal/products?ids=...` for line item snapshot enrichment.
- Implemented `CartClient`: best-effort `DELETE /cart/internal/carts/:userId` post-checkout cleanup.
- Implemented `MockPaymentProvider` and `PaymentsService`: authorizes and captures payment, generating unique transaction IDs.
- Implemented `CheckoutService`:
  - Redis idempotency checks via `idem:{key}` with 24-hour TTL and SHA-256 payload hashing.
  - Replays identical response without duplicate database inserts.
  - Rejects mismatched payload under same key with `409 IDEMPOTENCY_CONFLICT`.
  - In-flight lock `idem:{key}:lock` prevents concurrent race conditions with `409 IDEMPOTENCY_IN_PROGRESS`.
  - Pre-commit stock reservation with `CatalogClient`.
  - Saga-lite compensation: releases reserved stock if coupon validation, payment capture, or database transaction fails.
  - Single atomic PostgreSQL transaction (`BEGIN ... COMMIT`) inserting `orders`, `order_items` snapshots, `order_status_history`, `payments`, atomic `discount_codes` usage increment, and `outbox` row (`order.created`).
- Implemented `CheckoutController` with `POST /checkout` and dual-mount routes.
- 7 unit tests passed in `checkout.service.spec.ts` (28 total unit tests).
- 6 e2e tests passed in `checkout.e2e-spec.ts` (30 total e2e tests across 4 files).
- 15 atomic commits recorded in `order-svc`.
