# ca-003 — Cart entity and item CRUD (done, 2026-10-27)

## What

Implement the active-cart ensure path and the item operations the storefront
needs: add, update quantity, remove one, batch remove, clear, and read with
totals. Add idempotency and the one-event-per-mutation rule.

## How

- `src/cart/cart.repository.ts` — active cart by user/session, `23505`
  retry on insert, atomic line upserts with `NULLS NOT DISTINCT`, ownership
  scoped item reads/writes, and `last_activity_at` touches in the same
  transaction as each mutation.
- `src/cart/cart.service.ts` — catalog snapshots, cent-accurate totals,
  quantity/ownership decisions, and one post-commit `cart.updated` event.
- `src/cart/catalog.client.ts` — `CatalogClient` port + deterministic
  `FixtureCatalogClient`; `HttpCatalogClient` remains the production swap.
- `src/cart/idempotency.service.ts` + `idempotency.interceptor.ts` — Redis
  key scoped by identity, method, path, and client key; 24h TTL; replay on
  matching body; `409` on body conflict; fail-closed `503` on Redis read
  failure.
- `src/auth/guards/cart-identity.guard.ts` — verified JWT subject or
  `x-session-id` header/cookie; malformed tokens never fall back to guest.
- `src/auth/access-token.ts` + `auth.module.ts` — one JWT verification path
  shared by admin settings and shopper cart guards.
- `src/cart/cart.controller.ts` — `GET /cart`, item POST/PATCH/DELETE,
  batch delete, and clear.
- `src/events/event-bus.ts` — no-op adapter until Kafka exists.
- `src/redis/redis.service.ts` — ioredis with offline queue disabled.
- `test/cart.e2e-spec.ts` — guest/user ownership, snapshots, totals,
  replay/conflict, foreign item 404, batch/clear, one event, Redis-down 503.
- `src/cart/*.spec.ts`, `src/auth/guards/cart-identity.guard.spec.ts` —
  focused service, idempotency, totals, and identity unit coverage.

## Decisions

- Store product snapshots at add time — cart reads never join catalog.
  Rejected: live catalog lookup (couples services, breaks offline).
- Fail closed when Redis is unavailable for keyed mutations — a double-add
  is worse than a short 503. Rejected: best-effort dedupe.
- Scope idempotency keys by identity and route — a key must not replay
  another shopper's response or cross an endpoint. Rejected: global key.
- One `cart.updated` per mutation, after commit, fire-and-forget. Rejected:
  await the broker (latency + false failure).
- `qty = 0` is a removal via DELETE, not a PATCH value. Rejected: allowing
  zero rows.
- A Redis write failure after commit is logged but does not turn a
  successful mutation into an error response. Rejected: returning 503 after
  the database committed, which invites a duplicate retry.

## Verification

- `pnpm test`: 74 unit tests across 11 files green.
- `pnpm test:e2e`: 46 e2e tests across 5 files green; cart suite 20 tests.
- `pnpm exec tsc --noEmit`, `pnpm lint` (0 warnings), `pnpm build`: clean.
- Cart e2e covers guest header/cookie, verified user JWT, body-session
  rejection, missing idempotency key, replay/conflict, totals, same-product
  increment, foreign user/guest 404, single/batch/clear, unavailable
  product 422, Redis-down 503, and one event per committed mutation.
- Local cleanup verified: 0 carts, 0 cart items, settings still `global` /
  `{}` / version `0`; 0 `idem:*` Redis keys.
- cart-svc commits: `9eaaafe..404835e` (25 commits). All remain local;
  nothing pushed.

## Follow-ups

- Commit the existing uncommitted `cart-svc/src/app.module.ts` wiring
  (`CartModule` import + `JWT_SECRET` validation); HEAD still does not import
  `CartModule`.
- Add the production `HttpCatalogClient` and wire `catalog-svc`; the fixture
  adapter is the only v1 catalog source today.
- Replace the no-op event bus with Kafka and decide whether an outbox is
  needed for delivery guarantees; the current publish is fire-and-forget.
- A Redis death between the preflight read and the post-commit write can
  still leave a committed mutation without a replay record. Consider an
  atomic reservation/outbox if strict retry dedupe is required.
- Add Redis to readiness/observability and rate limits in `ca-006`.
