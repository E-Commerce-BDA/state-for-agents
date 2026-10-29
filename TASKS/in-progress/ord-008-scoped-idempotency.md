# ord-008 — order-svc: scope and harden Redis idempotency

## What

`x-idempotency-key` is currently a single global Redis key (`idem:{key}`). Two
customers who generate the same UUID can be served each other's order
confirmation, and because the cache is the only record, a crash between `COMMIT`
and `REDIS SET` produces a duplicate order. A Redis outage surfaces as a 500
instead of a retryable 503. This task moves the authority for "one key = one
order" onto the order row itself (`db/004`: `idempotency_key`,
`idempotency_body_hash`, partial unique index on `(user_id, idempotency_key)`),
scopes the Redis key by user and route, and makes Redis failures fail closed only
*before* the first durable write.

Status: in progress (claimed 2026-10-29).

## How

- `db/004-orders-idempotency.sql` — two nullable columns plus the partial unique index.
- `src/checkout/checkout.repository.ts` — all checkout SQL moves out of the service.
- `src/checkout/checkout.service.ts` — new guard order: hash → cache → lock → DB → write.
- `db/rows.ts` — `OrderRow` gains the two columns.
- Tests: `checkout.service.spec.ts` (mocked repository), `test/checkout.e2e-spec.ts`
  (real Postgres + Redis, incl. a second app with a throwing `RedisService`).

## Decisions (+ one rejected alternative each)

(pending)

## Verification

(pending)
