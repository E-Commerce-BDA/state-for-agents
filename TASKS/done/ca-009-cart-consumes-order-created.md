# ca-009 — cart-svc consumes `order.created` and converts the cart idempotently (done, 2026-11-01)

## What

Checkout converted a cart by calling cart-svc over HTTP — the Phase 0 bridge from `ca-007`
(`POST /cart/internal/carts/:userId/convert`). It worked, but it made a domain consequence
(converting a cart) into a synchronous dependency of checkout: the endpoint had to exist, be
authorised by a service key, and answer fast enough, for an order to be placed. `ord-011` had
already moved order-svc onto the outbox, and the caller was tolerating `404` from the bridge as
non-fatal, which was the signal that the call was never really required.

`ca-009` deletes the bridge and converts the cart from `order.created` instead, in one
transaction with a `cart.processed_events` claim, under consumer group `cart-svc`.

## How

- `db/004-cart-processed-events.sql` (new) — `cart.processed_events (event_id varchar(64) PK,
  topic varchar(64) NOT NULL, processed_at timestamptz NOT NULL DEFAULT now())` plus
  `idx_cart_processed_events_processed_at`. The exact shape `catalog.processed_events` (`006`)
  and `search.processed_events` (`003`) already have, because `@ecom/messaging`'s
  `ProcessedEventsStore` writes all three. Applied to `ecom` and `cart_test`.
- `src/events/order-created.handler.ts` (new) — `readEventEnvelope` →
  `parseEventPayload('order.created')` → one transaction:
  `claim(client, eventId, 'order.created')` (false ⇒ `duplicate`), then
  `CartRepository.convertForOrder(client, userId)`. `undefined` ⇒ `{ kind: 'ignored', reason:
  'no-active-cart' }` with the offset committed; otherwise `record(client, cart)` writes the
  `cart.updated` outbox row and the outcome is `applied`.
- `src/cart/cart.repository.ts` — `convertActiveCart(userId)` became
  `convertForOrder(client, userId)`: the same `UPDATE … status = 'converted' … RETURNING`, and
  the `record()` outbox write now happens **inside** the caller's transaction. The claim and the
  conversion therefore commit or roll back together.
- `src/cart/cart.service.ts` — `convertCart` deleted. Nothing in the HTTP path converts a cart
  any more.
- Deleted the bridge: `src/internal/internal.controller.ts`, `src/internal/internal.module.ts`,
  the `InternalModule` import in `app.module.ts`, and the six convert cases in
  `cart.service.spec.ts`.
- `test/internal.e2e-spec.ts` — rewritten to exactly one assertion: the old path answers `404`
  **with and without** `x-service-key`.
- `src/events/cart-consumer.controller.ts` (new) — `@EventPattern('order.created')` with
  `@Payload() raw: string, @Ctx() ctx: unknown`, delegating to
  `KafkaEventHandler.run(ctx, 'order.created', raw, …)`. One controller, one consumer, one
  commit protocol; a second topic (`ca-010`) becomes one more method, never a second group.
- `src/events/consumer-runtime.ts` (new) — `createKafkaConsumerStrategy({ brokers, clientId:
  'cart-svc', groupId: 'cart-svc' })` + `connectMicroservice` + `startAllMicroservices`,
  guarded by `KAFKA_CONSUMER_ENABLED` (default `true`, `false` in the e2e config). A broker that
  is down retries every 5 s and `main.ts` does not await the start: refusing to serve a shopping
  cart because Kafka is restarting would be worse than a cart that converts seconds later.
- `src/app.module.ts` Joi schema + `.env.example` — `KAFKA_CONSUMER_ENABLED`.

## Decisions

1. **Conversion is a domain consequence, not a checkout dependency.** Rejected: keep the
   synchronous HTTP call — it couples checkout availability to cart, and order-svc already had
   to swallow its `404`.
2. **The claim rides the conversion's transaction, not a separate one.** A claim that commits
   without the conversion makes a redelivery a silent no-op with an unconverted cart; a
   conversion without the claim double-converts on redelivery. Rejected: Redis-only dedupe,
   which is lost on flush.
3. **"No active cart" is `ignored` + committed, never a DLQ record.** A shopper who checks out
   without ever building a cart is normal traffic. Rejected: dead-letter it — that turns ordinary
   traffic into an operational queue and hides real poison records.
4. **Contracts stay at `1.8.0`.** `order.created`'s payload is unchanged since 1.7.0 and cart
   parses no `product.*` payload, so there is nothing in `1.9.0` to adopt. Fewer moving parts.
   Consequence: `@ecom/messaging 0.3.0` declares `@ecom/contracts >=1.9.0 <2`, so cart runs one
   floor below its peer range. pnpm resolves it and every suite is green; recorded as known debt
   in `8.Versioning.md §10`.
5. **Delete the bridge rather than keep it beside the consumer.** Two live conversion paths is
   the defect this task exists to remove, and a deprecated endpoint that still works is one
   somebody will call. The e2e spec now proves the deletion (`404` with and without a service
   key) instead of proving the behaviour.
6. **No `/consumer-stats` endpoint.** The counters exist in-process in the shared
   `KafkaEventHandler`, but exposing them was not in this task's surface; the group is observable
   through `kafka-consumer-groups.sh`. Named debt, not coverage.

## Verification

| Check | Result |
|---|---|
| `cart-svc` `pnpm test` | 119 passed (17 files) |
| `cart-svc` `order-created.handler.spec.ts` | 8 cases: applied, duplicate, invalid-envelope, invalid-payload, no-active-cart ignored, claim + convert + outbox in one transaction, a throw leaves no claim, another user's cart is a no-op |
| `cart-svc` `cart-consumer.controller.spec.ts` | 10 cases through the real `@EventPattern` wiring |
| `cart-svc` `test/order-created.e2e-spec.ts` | converted cart + exactly one `cart.outbox` row + exactly one `cart.processed_events` row; a replay writes neither a second row nor a second event |
| `cart-svc` `test/internal.e2e-spec.ts` | exactly one assertion: `404` with and without `x-service-key` |
| `cart-svc` `pnpm test:e2e` | 96 passed, 2 skipped (12 files passed, 2 skipped — both live Kafka specs are gated on `RUN_KAFKA_E2E`) |
| `cart-svc` `pnpm test:e2e` with `RUN_KAFKA_E2E=1 -- live-kafka.order-created` | 3 passed against `ecom-kafka` |
| `cart-svc` `pnpm lint` | 0 warnings, 0 errors (81 files) |
| `cart-svc` `npx tsc --noEmit` | exit 0 |
| `cart-svc` `nest build` | clean |
| commit | `cart-svc` `f707431` |

## Open

- **Named debt:** order-svc's `CartClient` still calls the deleted endpoint and will log a `404`
  warning on every checkout until `ord-012` removes the caller. `CartClient` treats `404` as
  non-fatal — that is precisely why this task could land first — and the existing order-svc test
  that proves a failed conversion never fails checkout stays green.
- No `/consumer-stats` route (§ Decisions 6). Until one exists the group is observable only from
  the CLI.
- `cart.processed_events` has no retention sweeper; the index on `processed_at` exists so a
  future one can prune without a full scan.
- The peer-floor mismatch in § Decisions 4 closes the next time cart repins contracts for any
  other reason.
