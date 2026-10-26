# ca-005 — Wishlist (todo)

## What

Implement the user-only wishlist endpoints on top of the existing
`wishlists` / `wishlist_items` tables.

## How

- `src/wishlist/wishlist.repository.ts` — one wishlist per user; unique
  `(wishlist_id, product_id)`.
- `src/wishlist/wishlist.service.ts` — list/add/remove.
- `src/wishlist/wishlist.controller.ts` — `GET /wishlist`,
  `POST /wishlist/items`, `DELETE /wishlist/items/:id`.
- `test/wishlist.*` — auth required, duplicate add idempotent, remove,
  empty list.

## Decisions

- User-only in v1 — no guest wishlist. Rejected: session wishlist (merge
  rules and cleanup add complexity without a shopper requirement).
- No `cart.updated` event — wishlist is not a cart. Rejected: reusing the
  cart event (pollutes analytics).
- Keep product snapshots out of wishlist — only the product id is stored.
  Rejected: duplicating cart snapshot fields.

## Verification

Pending. Gate: unit + e2e green, `tsc --noEmit`, `oxlint`, `nest build`.
