# sf-053a — storefront: live checkout e2e harness

- Repo: `frontend/storefront`
- Phase: P5 · priority: P2 · kind: test
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit: `1b50c9a` — verified the harness and fixed its broken assertions
- Verified: **2026-11-26 against the live stack**

## What

The harness now signs the shopper in through the public `/signin?next=/cart`
route, merges the guest cart, places the order through the real browser, and
asserts the 201 body's order id rather than a confirmation URL. The cart DELETE
from the island is suppressed during conversion testing so the assertion
genuinely tests the `order.created` consumer. README claims were corrected to
match the actual probe and replay paths.

## Verification (live)

`pnpm test:e2e:live` against the live stack and the webpack production build
finished **exit 0** with `PASS: order c3c6bc99-…-dcdcddfc4a13, replay matched,
cart converted`. No failures, no skips — the stack-up probe fired, not the skip
branch.

Assertions that ran and passed:

1. Auth, cart, catalog, order and storefront all reachable.
2. Product seeded through the catalog admin API (active, stock 25).
3. Shopper registered through auth-svc.
4. Browser sign-in via the public route with guest→account cart merge.
5. PDP add-to-cart, then cart → checkout through the real browser.
6. `POST /api/checkout` → 201 with an order id; idempotency key captured.
7. Same key and body replay → identical confirmation body.
8. Cart emptied with the island's own DELETE suppressed → only the
   `order.created` consumer could have converted it.

Gates: lint 0 errors / 40 pre-existing warnings, typecheck clean, 1382 tests in
185 files, webpack build green. The next-dev-generated `AGENTS.md` rules block
was committed with the work so the tree stays clean.

## Caveats

- "No second order or charge" is established by identical replay body and the
  captured key, **not** by a database count of orders/charges.
- The confirmation route has a real storefront race: the island's empty-cart
  effect can replace the pushed URL with `/cart` even though the order succeeded.
  Flagged, not fixed — out of scope for this task; worth a separate ticket.
- Environment workarounds, not product changes: Nest `start:dev` emits
  `dist/src/main.js` so compiled entries were run directly; `next dev`
  Turbopack panics on `globals.css` so webpack dev/build were used; the dev DB
  needed `catalog-svc/db/010-product-popularity.sql`; Playwright 1.64.0 was
  installed in a temp dir and junctioned into `node_modules` without touching
  the lockfile; an admin JWT was made via a temporary admin user and role grant.

## Follow-ups

- Ticket the checkout confirmation-route race separately.
- If desired, strengthen the replay assertion with a DB count of orders/charges.
