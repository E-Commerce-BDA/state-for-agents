# ord-008 — order-svc: scope and harden Redis idempotency

## What

`x-idempotency-key` was a single global Redis key (`idem:{key}`) and the cache
was the only record of a checkout attempt. Two customers who generated the same
UUID could be served each other's confirmation; a crash between `COMMIT` and
`REDIS SET` produced a duplicate order on retry; and a Redis outage surfaced as a
500 instead of a retryable 503.

The identity now lives on the order row: `db/004` adds `idempotency_key` and
`idempotency_body_hash` plus a **partial unique index on `(user_id,
idempotency_key)`**, and the Redis key is scoped to
`idem:{userId}:checkout:{key}`. Redis keeps only the replay cache, a cached
response is replayed only when the order it names still exists, and Redis
failures fail closed *before* the first durable write and are ignored after it.

## How

- `db/004-orders-idempotency.sql` — two nullable columns, `idx_orders_idem` (`UNIQUE (user_id, idempotency_key) WHERE idempotency_key IS NOT NULL`).
- `src/db/rows.ts` — `OrderRow` carries both columns.
- `src/common/canonical-json.ts` — key-sorted JSON, so the body hash is about the request and not about serialisation order.
- `src/checkout/checkout.repository.ts` — every checkout statement (order, items, history, payment, coupon usage, outbox) in one transaction, with constraint discrimination.
- `src/checkout/checkout.service.ts` — guard order is hash → cache → lock → database → write; compensation for the losing attempt.
- `src/checkout/checkout.module.ts` — provides `CheckoutRepository`.
- Tests: `checkout.service.spec.ts` (mocked repository), `canonical-json.spec.ts`, `test/checkout.e2e-spec.ts` (real Postgres + Redis), and `test/orders.e2e-spec.ts` now applies every migration in filename order.

## Decisions (+ one rejected alternative each)

- **The order row is the authority; Redis is a cache.** `findByIdempotencyKey(user, key)` answers "did this happen", and a cache entry is only replayed when the row it names exists. Reason: the cache was the only record, so a restored dump or an eviction could either invent an order or lose one. Rejected: keep Redis as the only record and simply scope the key.
- **A cache hit is verified, not trusted.** One PK-scoped read on replay buys the guarantee that the cache cannot outlive the row. Rejected: replay straight from the cache to save the round trip.
- **Fail closed only before the first durable write.** Pre-flight Redis failure → `503 IDEMPOTENCY_UNAVAILABLE` (nothing happened, retry with the same key); a failure after commit is a warning and the `201` stands. Rejected: a uniform 503, which hides a real order behind an error and makes clients double-order after the outage.
- **The unique index is the concurrency gate, not the lock.** The lock only serialises; the race is settled by `idx_orders_idem`, and the loser compensates its own capture (provider refund) and its own hold, then serves the winner's confirmation. Rejected: letting the `23505` bubble up — the loser's customer would be charged for an order nobody wrote.
- **Body hash over canonical JSON.** `JSON.stringify(dto)` follows the client's key order, so a reordered but identical payload looked like a conflict. Rejected: hashing the raw serialisation.
- **Two unique constraints, two meanings.** `createOrder` inspects `err.constraint`: `orders_order_number_key` ⇒ redraw the six-digit number and replay the transaction (max 3), `idx_orders_idem` ⇒ `DuplicateIdempotencyKeyError`, anything else ⇒ rethrow. Reason: a random six-digit number collides eventually, and a 500 after a capture is expensive. Rejected: a DB sequence for order numbers (new schema object, enumerable numbers) and "hope it never happens".
- **The reservation id doubles as the provider idempotency key.** It is generated locally, stable across the attempt, and unique — unlike the shared `'order-temp'` literal. Rejected: keep the literal.
- **Errors are payload objects** (`{ code, message }`) so `error.code` survives the 5xx mask, and the stock failure keeps its real code (`INSUFFICIENT_STOCK`) instead of collapsing to `CONFLICT`. Rejected: the old `'CODE: message'` strings.
- **A `pending` stored attempt answers `409 IDEMPOTENCY_IN_PROGRESS` for now**; `ord-009` replaces that branch with resumption, which is only meaningful once the saga can leave a pending row behind. Rejected: pretending a pending order is a completed replay.

## Verification

All commands from `order-svc` on 2026-10-29:

| Gate | Result |
|---|---|
| `pnpm lint` (oxlint --type-aware) | 68 files, 0 warnings, 0 errors |
| `pnpm test` | 6 files / 61 tests passed (14 new checkout cases + 4 canonical-json) |
| `pnpm test:e2e` | 6 files / 67 passed, 1 skipped (live catalog) — checkout 13 + 1 skipped |
| `pnpm build` (`nest build`, includes `tsc --noEmit`) | clean |
| `psql` | `idx_orders_idem` present: `UNIQUE (user_id, idempotency_key) WHERE (idempotency_key IS NOT NULL)` |

Behaviour proven by `test/checkout.e2e-spec.ts`:
same user + key + body replays the same `orderId`/`orderNumber` with one order
row; **two customers with the same key get two independent orders**; replay
still works after the cache entry is deleted (the row answers); a different body
is a `409 IDEMPOTENCY_CONFLICT` even with the cache gone (the stored hash
answers); two concurrent identical requests write exactly one order; and a
second app whose `RedisService` throws returns `503 IDEMPOTENCY_UNAVAILABLE`
with **no** order row.

Commits: `ac7ab45` db/004 · `7a5b72a` row types · `41708c1` canonical json ·
`9e03be2` repository · `8c2fc50` guard · `4c43f8d` fixture · `b5b1cc4` +
`c8fb302` unit specs · `66852c5` + `08e7fd8` e2e.

## Follow-ups

- `ord-009`: replace the `pending` branch with saga resumption, and add `confirmOrder`/`failOrder` to the repository (they land with their callers, not before).
- `cart-svc` still uses a bare `idem:{key}`; `ca-007`/`ec-002` should adopt the same `(user, route, key)` scope.
- Once every keyed mutation reads the row first, the pre-flight lock can be reduced to a best-effort hint.
