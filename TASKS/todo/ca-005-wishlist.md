# ca-005 — Wishlist (todo)

## What

Implement the customer wishlist endpoints on top of the existing
`wishlists` / `wishlist_items` tables.

## How

- Docs-first: `Documentation/services/cart.md` §4.8/§7.1/§7.2,
  `Documentation/4.API-Design.md` §4.13, `Documentation/services/auth.md`
  §1/§3, `Documentation/5.Features.md` A3.6/A6.5, `Documentation/9.Testing.md`
  §3.3.
- `src/wishlist/wishlist.repository.ts` — one wishlist per user; unique
  `(wishlist_id, product_id)`; product-level, no `variant_id`.
- `src/wishlist/wishlist.service.ts` — list/add/remove; duplicate add
  returns the existing item; foreign/missing delete →
  `404 WISHLIST_ITEM_NOT_FOUND`; `GET` never creates a wishlist row.
- `src/wishlist/wishlist.controller.ts` — `GET /wishlist`,
  `POST /wishlist/items`, `DELETE /wishlist/items/:id`; `JwtAuthGuard` +
  `RolesGuard` + `@Roles('customer')`.
- `test/wishlist.*` — 401/403/200, duplicate, product-level uniqueness,
  foreign delete, no event, GET read-only.
- Storefront guest flow is a separate slice: prompt sign-in, keep pending
  product id via `?next=`/short-lived cookie (never `localStorage`), POST
  after login.

## Decisions

- Verified JWT + `customer` role, checked in cart-svc; no guest wishlist.
  Guests use a sign-in prompt + pending product id. Rejected: session
  wishlist (merge/cleanup complexity without a shopper requirement).
- Service re-verifies the JWT and scopes SQL by `user_id = JWT.sub`; never
  trusts `x-roles`. Admin-only tokens get 403; admins who shop also hold
  `customer`.
- Product-level, not variant-based; variant choice happens at add-to-cart.
- No `cart.updated` event — wishlist is not a cart. Rejected: reusing the
  cart event (pollutes analytics).
- No product snapshots — only the product id is stored; storefront hydrates
  from catalog.
- Duplicate add returns the existing item; no `x-idempotency-key`.
- Add/remove touches `wishlists.updated_at` explicitly in the same
  transaction; the existing trigger covers direct wishlist-row updates only.

## Verification

Pending. Gate: unit + e2e green, `tsc --noEmit`, `oxlint`, `nest build`.
