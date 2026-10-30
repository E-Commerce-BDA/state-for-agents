# ca-007 — cart conversion bridge (in progress)

## What

Checkout called `DELETE /api/v1/cart/internal/carts/:userId` and cart-svc served no
internal route at all, so the call 404ed in silence and every completed order left the
cart active. This task adds the endpoint the caller already believed in.

## How

- cart-svc `src/auth/guards/service-key.guard.ts` — `x-service-key` vs
  `INTERNAL_SERVICE_KEY`, 401 `{code:'SERVICE_KEY_INVALID'}`, exported from `AuthModule`.
- `app.module` Joi: `NODE_ENV` + `INTERNAL_SERVICE_KEY` (16+, `Joi.required()` when
  `NODE_ENV=production`, documented dev fallback otherwise).
- `CartRepository.convertActiveCart(userId)` — one `UPDATE … WHERE user_id=$1 AND
  status='active' RETURNING <CART_COLUMNS>`.
- `CartService.convertCart(userId)` — returns `{cartId, convertedAt}` or `null`, publishes
  one `cart.updated` through the existing bus.
- `src/internal/{internal.controller,internal.module}.ts` — `@Controller('cart/internal')`
  + `@UseGuards(ServiceKeyGuard)`, `POST carts/:userId/convert`, `ParseUUIDPipe`, 200/204.
- order-svc `CartClient.convertCart` — `POST …/convert`, `x-service-key`, 2 s
  `AbortSignal.timeout`, warn on `!ok`, never throws; checkout calls it fire-and-forget.

## Decisions

1. **One UPDATE, no transaction.** `one_active_cart_per_user` (partial unique index) proves
   at most one row, so `FOR UPDATE` and a transaction buy nothing.
   Rejected: `SELECT … FOR UPDATE` like the merge path — that path touches two carts.
2. **204 instead of 404 for an empty result.** A replay and a user who never had a cart are
   the same fact; 204 keeps the caller's log clean and makes the call idempotent without a
   key. Rejected: 409/404, which would make every replay an alert.
3. **Convert, never delete.** Items stay for analytics and support; `converted` is the audit
   state the merge path already uses. Rejected: `DELETE FROM cart.items`, which loses history.
4. **Production refuses to boot without a key.** The guard keeps a dev fallback for local
   e2e, so the fallback has to be impossible in a deployment — Joi enforces it at startup
   instead of trusting the deployment. Rejected: a hard-coded key, which is a published
   secret.
5. **The bridge is HTTP, not the future consumer.** ca-009 owns the `order.created` consumer;
   until then checkout must not depend on a broker. Rejected: waiting for ca-009, which
   leaves every order with an active cart.
6. **Client warns instead of throwing.** A failed conversion costs an abandoned-cart email,
   never the order. Rejected: retry/throw, which would fail a paid order over a cart.

## Verification

| Check | Result |
|---|---|
| cart-svc `pnpm lint` | 0 warnings, 0 errors |
| cart-svc `pnpm test` | 91 passed (14 files) |
| cart-svc `pnpm test:e2e` | 87 passed (9 files, incl. the new 8-case internal spec) |
| cart-svc `pnpm build` | clean |
| order-svc `pnpm lint` / `test` / `build` | 0/0, 81 passed, clean |
| order-svc `pnpm test:e2e` | 76 passed, 1 skipped (DB fixture reset needed, see Open) |

## Open

- `SAVE10` was exhausted (`uses_count = max_uses = 100`) in the dev database, so checkout
  e2e returned 422 until the row was reset. The seed needs `ON CONFLICT … DO UPDATE`.
- ord-012/ca-009 delete this bridge.
- `4.API-Design.md` §6 still keys `cart.updated` by `userId|sessionId`; the 1.4.0 registry
  says `cartId`.
