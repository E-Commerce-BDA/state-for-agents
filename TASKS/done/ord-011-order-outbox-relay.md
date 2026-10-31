# ord-011 — order-svc: real Kafka outbox relay for order events (done, 2026-10-31)

## What

order-svc had an `order.outbox` table and an `OutboxService.dispatchEvent` that logged the
event and then marked the row `published`. Consumers existed (`cat-009` commits the stock hold
from `order.created`) but no record ever reached a broker, so in a real deployment a paid
order's hold expired after 900 s and the item could be sold twice. This task replaces the
log-only dispatcher with `@ecom/messaging` 0.2.0: `order.created` and `order.status.updated`
are written by the write site with the transaction's client, and the shared relay publishes
the stored envelope, marks it published only after the broker acks, and backs off / parks on
failure exactly like auth and cart.

`order.outbox` also had to change shape before it could be used at all: it stored a bare
`payload` rather than a finished envelope, and `order` is a reserved word, so the package's
unquoted `${schema}.${table}` was a syntax error against it. The quoting fix shipped in
`@ecom/messaging` 0.2.0 is what makes this task reachable.

## How

- `db/006-order-outbox-envelope.sql` — `ADD COLUMN envelope jsonb NULL`, `locked_until`,
  `last_error`; `ALTER COLUMN payload DROP NOT NULL`; pre-envelope pending rows are parked at
  `failed` with `last_error = 'pre-envelope row (migration 006)'`; three `CHECK`s
  (`status <> 'pending' OR envelope IS NOT NULL`, `envelope->>'type' = event_type`,
  `envelope->>'id' = event_id::text`); `idx_outbox_pending (created_at) WHERE status =
  'pending'` recreated.
- `src/outbox/order-outbox.ts` (+ `order-outbox.module.ts`) replaces `outbox.service.ts`,
  `outbox.repository.ts`, `outbox.module.ts` and `outbox.service.spec.ts`:
  - `recordOrderCreated(client, write, order)` — topic `order.created`, aggregate `order`,
    aggregate id `order.orderId`, `occurredAt` from `payload.createdAt`.
  - `recordStatusUpdated(client, payload: OrderStatusUpdatedPayload)` — topic
    `order.status.updated`, `occurredAt` from `payload.timestamp`.
  - `OrderCreatedWrite = { topic: 'order.created'; payload: (order: OrderIdentity) =>
    OrderCreatedPayload }` — the payload cannot be built before the insert, because the order
    number only exists after `INSERT ... RETURNING`, so the repository resolves a builder
    inside the transaction.
- Write sites, all passing the transaction's client:
  - `checkout.repository.ts` — `CreateOrderInput.outbox` (typed, currently `null` on the TX1
    pending insert) and `confirmOrder`'s `outbox` argument, which is the live path: the event
    is written in TX2 after capture, so `order.created` never announces an unpaid order.
  - `orders.repository.ts` (`updateStatusWithHistory`) — replaces the hand-built payload.
  - `refunds.repository.ts` (`refund`) — one `order.status.updated {to:'refunded'}`, no
    `order.refunded` event.
- `src/app.module.ts` — `createOutboxModule({ schema: 'order', producer: 'order-svc',
  clientId: 'order-svc', pool: getPool })`, with a comment saying it only works because 0.2.0
  quotes the identifiers.
- Deps: `@ecom/contracts` 1.8.0, `@ecom/messaging` 0.2.0, `kafkajs` ^2.2.4; `.env` /
  `.env.example` gained `KAFKA_BROKERS` and `DISABLE_OUTBOX_RELAY`.
- Tests: `test/outbox.e2e-spec.ts` (row shape, drain, retry-to-`failed`, rollback), the
  `schema.e2e-spec.ts` insert into `"order".outbox` updated for the new columns,
  `test/live-kafka.e2e-spec.ts` gated on `RUN_KAFKA_E2E=1`.

## Decisions

1. **Reuse the table instead of creating `order.outbox_v2`.** The old rows are the only record
   of what consumers already received, so they are kept and parked; `payload` stays, nullable.
   Rejected: `DROP COLUMN payload`, which destroys that record (D6 in the plan).
2. **Park pre-envelope rows at `failed`, not `pending`.** They can never be published as 1.8.0
   envelopes, and leaving them pending would burn five attempts each on every relay start.
   Rejected: build an envelope at publish time from the old payload — the relay re-derives
   nothing, by design.
3. **A builder, not a payload, in `CreateOrderInput`.** `orderNumber` does not exist until the
   insert returns, and building it outside the transaction would be a race. Rejected: have the
   service construct the payload and pass it in, which cannot work for a value the row mints.
4. **`order.created` is written after capture (TX2), not when the order row is inserted (TX1).**
   The order is `pending` until the provider answers; announcing it earlier would tell catalog
   to commit a stock hold for an order that may be declined. Rejected: emit on the pending
   insert and follow with a compensating event.
5. **Delete the old outbox service rather than leaving it beside the relay.** Two write paths
   into one table, one of which never publishes, is the drift this task removes. Rejected:
   keep `dispatchEvent` as a no-op "for compatibility".
6. **Keep `order.status.updated` for refunds.** One lifecycle event family, one consumer path;
   `order.refunded` was already dropped at design time. Rejected: a second event type.

## Verification

| Check | Result |
|---|---|
| `pnpm build` | exit 0 |
| `pnpm lint` | 0 warnings / 0 errors (71 files) |
| `pnpm test` | 78 passed |
| `pnpm test:e2e` (relay disabled) | 82 passed, 3 skipped |
| `test/outbox.e2e-spec.ts` | one pending row per confirmed order with `envelope.type = 'order.created'`; drain → `published` with `published_at`; a `PATCH .../status` writes `order.status.updated`; a forced failure after the outbox write leaves neither order row nor outbox row |
| `RUN_KAFKA_E2E=1 pnpm test:e2e -- test/live-kafka.e2e-spec.ts` | 2/2 — `order.created` (checkout) and `order.status.updated` (`PATCH /api/v1/order/orders/:id/status`) consumed from the real broker |
| `kafka-console-consumer` (in `ecom-kafka`) | one record on each topic, `producer: order-svc`, key = `orderId`, envelope parses |
| dotted identifier | `createOutboxModule({ schema: 'order' })` runs at boot; before 0.2.0 the unquoted `order.outbox` was a syntax error |
| commit | `order-svc` `d76d10f` |

## Open

- Committed on 2026-10-31 as `d76d10f`. The gate re-run that day was lint (0/0, 71 files), 78
  unit tests in 6 files and `nest build`; e2e was **not** re-run because the compose stack was
  down, so the 82 + 3 skipped above is the 2026-10-31 run. `order.outbox` gained readable tables
  but `payload` is still there for historical rows; a later cleanup can drop it once every
  environment's rows are `published` or `failed`.
- `order.outbox` has no retention sweep and no metrics endpoint.
- `ord-012` (retire the cart convert bridge) now depends only on `ca-009`.
- The relay is disabled in every e2e run (`DISABLE_OUTBOX_RELAY=true`); only the gated live
  spec proves the real broker path.
