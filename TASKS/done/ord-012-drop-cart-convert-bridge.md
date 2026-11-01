# ord-012 — the cart convert bridge is gone (done, 2026-11-01)

## What

`ca-009` deleted `POST /internal/carts/:userId/convert` from cart-svc when conversion
moved to the `order.created` consumer, but order-svc kept calling it. Every checkout
therefore POSTed to a dead route and logged one `404` warning per order — noise that
looked like a transient failure and hid real ones.

ord-012 removes the caller: `CartClient`, its module wiring, the call site and
`CART_SVC_URL`. Conversion now has exactly one owner, cart-svc's own `order.created`
consumer, which converts inside one transaction with a `cart.processed_events` claim.

The tracker entry's stored rationale was stale in the other direction — it said the call
could not be removed yet because the endpoint did not exist. Both halves were wrong at
different times; the entry now records what actually happened.

## How

- `order-svc/src/clients/cart.client.ts` and `cart.client.spec.ts` — deleted.
- `order-svc/src/clients/clients.module.ts` — `CatalogClient` only, docstring rewritten
  to say why there is no cart client.
- `order-svc/src/checkout/checkout.service.ts` — the `CartClient` import and the
  constructor parameter removed; the bridge call replaced by a comment naming the
  consumer that does the work.
- `order-svc/src/checkout/checkout.service.spec.ts` — the cart mock deleted; new
  `describe('cart conversion (ord-012)')` asserts `globalThis.fetch` is never called
  during a confirmed order.
- `order-svc/src/app.module.ts`, `.env`, `.env.example` — `CART_SVC_URL` removed from
  the Joi schema and both env files.
- `order-svc/db/002-seed-orders.sql` — a separate commit (`5fd303b`): `SAVE10` seeds
  `max_uses = 100` and each coupon checkout spends one, so `ON CONFLICT DO NOTHING`
  exhausted the fixture after ten e2e runs and made eleven checkout cases and two
  discounts cases answer `422 COUPON_INVALID`. The seed now upserts.
- `Documentation/services/order.md`, `Documentation/services/cart.md` — the bridge
  removed from the flow, the known-issue row struck through as resolved.

## Decisions (+ one rejected alternative each)

1. **Delete the client, not just the call.** A client kept "for later" is a client
   somebody calls; the whole point is that conversion is not an HTTP concern of
   checkout. Rejected: leave it as dead code behind a flag — the flag would still fire
   the request unless somebody remembered to turn it off.
2. **Delete `CART_SVC_URL` too.** A config variable with no reader invites the client
   back as a quick fix. Rejected: keep it for a hypothetical future cart call — a real
   future call would be an event.
3. **Prove the absence, not the behaviour.** The new spec asserts that a confirmed
   checkout makes no outbound HTTP call at all, so the bridge cannot come back without
   failing a test. Rejected: assert `convertCart` is not called — that requires the
   method to still exist.
4. **Fix the fixture, not the assertions.** The `422` failures were the seed's fault
   (a coupon budget consumed by previous runs), not the code's. Rejected: raise
   `max_uses` (a bigger collision, same defect) or truncate the coupon table (deletes
   rows other suites rely on).

## Verification

| Check | Result |
|---|---|
| `order-svc` `pnpm test` | 75 passed (5 files) |
| `order-svc` `checkout.service.spec.ts` | 26 cases, including no outbound fetch during a confirmed order |
| `order-svc` `pnpm test:e2e` | 82 passed, 3 skipped (7 files passed, 1 skipped) |
| `order-svc` `pnpm exec tsc --noEmit` | exit 0 |
| `order-svc` `pnpm lint` | 0 warnings, 0 errors (69 files) |
| `order-svc` `nest build` | clean |
| Conversion still happens once | `cart-svc/src/events/cart-consumer.controller.ts` (`@EventPattern('order.created')`) → `order-created.handler.ts` claim → `convertForOrder`, gated by `KAFKA_CONSUMER_ENABLED` (default `true`) |
| commit | `order-svc` `05d5402` (bridge), `5fd303b` (fixture), docs `4d3149e` |

## Open

- `cart-svc`'s `KAFKA_CONSUMER_ENABLED` must stay `true` wherever checkout runs. If it
  is ever turned off, carts silently stop converting and nothing in order-svc notices —
  the trade this task accepted when it made conversion async.
- The e2e suite still needs the payload-sensitive coupon fixture to be re-seeded
  (`pnpm db:seed` in order-svc) after a run spends `SAVE10`'s budget.
