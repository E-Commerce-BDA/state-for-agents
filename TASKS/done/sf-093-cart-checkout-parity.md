# sf-093 — Cart, checkout and confirmation compose OrderSummaryCard, Timeline, PaymentPill and QuickPromos while preserving BFF error details, coupon, idempotency and 409 shortfall handling

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 833f2df

## What

Cart, checkout and confirmation compose OrderSummaryCard, Timeline, PaymentPill and QuickPromos while preserving BFF error details, coupon, idempotency and 409 shortfall handling.

## Why

New painters take resolved data; totals and promo validation stay in pure lib. Rejected re-deriving totals in UI.

## Verification

Coordinator verified clean tree, author identity and four gates after each
commit. Final storefront suite: 242 files / 1627 tests, lint 0 errors
(40 pre-existing warnings), tsc clean, webpack build green. Agent served
storefront.html and next dev locally; auth and styled 404 were browser-captured.

## Follow-ups

- Full visual parity requires live auth/cart/order services.
