# cat-008 — catalog-svc consumes `product.imported`; the consumer moves to the shared transport (done, 2026-11-01)

## What

Two halves, one commit.

**The new route.** Nothing on the platform consumed `product.imported` on the catalog side, so an
import — the real data path for every product an admin did not type in — published an event that
only search-svc read. Catalog's own tables stayed empty until somebody created the product by
hand. `cat-008` makes the import a writer into `catalog`: product, category, brand, variants and
images, plus a stock movement, in one transaction with a `processed_events` claim.

**The transport migration.** catalog's `order.created` consumer was `cat-007`'s hand-written
`kafkajs` loop — correct, but the third copy of the same protocol (search had one, cart was about
to get one). It moves onto `@ecom/messaging 0.3.0` and the Nest Kafka transport, on **one**
strategy with **two** `@EventPattern`s, so `catalog-svc` is one consumer group rather than two
groups splitting the partitions.

## How

- `src/events/catalog-consumer.controller.ts` (new) — `@EventPattern('order.created')` and
  `@EventPattern('product.imported')` on the same controller, each with
  `@Payload() raw: string, @Ctx() ctx: unknown`, both delegating to
  `KafkaEventHandler.run(ctx, topic, raw, …)`. `OrderCreatedHandler` is **untouched**; only the
  transport around it changed.
- `src/events/kafka-order-consumer.ts` + its spec — deleted after every surviving behavioural
  case was re-pointed at the new controller + `ecom-messaging/test/consumer/*`. The cases were
  re-pointed, not dropped (see Decisions 4 and 5 for the two that could not survive verbatim).
- `src/events/product-imported/product-imported.handler.ts` (new) — envelope → payload →
  money-string coercion, then **one** transaction: claim, resolve category, resolve brand, upsert
  product, upsert variants, replace images, write stock movements.
- `src/events/product-imported/product-import.repository.ts` (new) — the write half. Deliberately
  not `ProductsRepository`: that is the HTTP path's writer and it owns presentation columns an
  import must never touch.
- `src/events/product-imported/import.errors.ts` (new) — `ProductImportRejectedError` with the
  four DLQ reasons; thrown, so the claim rolls back, and translated by `translateError` into an
  immediate dead letter instead of a 31-second retry ladder.
- `db/008-product-import-source.sql` (new) — widens `products_source_check` to accept `'import'`.
- `src/events/consumer-metrics.ts` + `consumer-stats.controller.ts` — the counters delegate to the
  package (nine names, the old five unchanged); `lag`, `totalLag`, `lastCommit` and `sampledAt`
  are additive.
- `src/events/consumer-runtime.ts` — `CONSUMER_GROUP_ID = 'catalog-svc'`, one strategy, retried
  start, `KAFKA_CONSUMER_ENABLED`.

## Decisions

1. **One consumer, one group, two routes.** A second `ServerKafka` for `product.imported` would
   be a second member of a different group over the same partitions, and the two routes would
   then need two offset policies. Rejected: one consumer per topic.
2. **No outbox row on import** (`D2`). search-svc already subscribes to `product.imported`, so
   re-emitting `product.updated` per row would turn a 10 000-row import into 10 000 extra events
   describing a change the index is about to receive anyway. Rejected: emit for uniformity —
   and written down so nobody later "fixes" the missing emit.
3. **`onHand = max(0, imported − openReserved)`.** `products.stock` and `product_variants.stock`
   are live on-hand already net of holds, because reserving decrements them at hold time; a feed
   reports *physical* stock. `openReserved` counts every `held` reservation **including holds past
   their expiry the sweeper has not reached**, because those units are still deducted and are
   about to be given back — subtracting them now is what stops the sweep double-counting them.
   Clamping at zero and warning is the honest failure; refusing the import would leave the
   product unpriced and unbuyable. Rejected: write the raw figure and let the sweep fix it.
4. **A dangling reference is a dead letter, not a guess.** `categoryId` / `brandId` must exist
   (`unresolved-reference`); only a *name* creates one (`ON CONFLICT (slug) DO NOTHING` plus a
   re-read, so concurrent imports share a row). A `sku` or `slug` held by another product id is
   `sku-conflict` / `slug-conflict`, and a variant `sku` belonging to another product is
   `variant-sku-conflict` — rewriting its `product_id` would move a live cart line to another
   product. Rejected: `ON CONFLICT` upsert by sku, which is exactly the silent overwrite.
5. **Variants are never deleted for being absent.** Absence is ambiguous ("the feed stopped
   selling it", "the array was omitted", "a partial import") and a deleted variant takes its stock
   movements with it (`ON DELETE CASCADE`). Withdrawal is a human decision.
6. **Images are a replace-set, product level only.** `imageRefSchema` is a bare string, so a
   payload cannot say which variant an image belongs to. Three ordered steps because
   `one_primary_per_product` is a partial unique index: clear the old primary first, delete the
   urls that are gone, then upsert with `sort_order = index` and `is_primary = index === 0`.
   Rejected: insert-then-delete, which violates the index.
7. **An update never rewrites `source`, `external_id`, `photo_settings`, `card_settings`,
   `tags`, `attributes`.** An import states what a product *is*, not how it looks or where it came
   from. A new row is stamped `source = 'import'`.

## Two behavioural deltas, recorded rather than hidden

The transport change is behaviour-preserving for `OrderCreatedHandler`, but not for every one of
`cat-007`'s spec cases, and both differences are deliberate:

1. **An unrouted topic cannot reach a Nest controller.** `cat-007`'s consumer saw every record it
   was subscribed to and could classify an unknown type in its own loop; here the strategy only
   subscribes the declared `@EventPattern`s, so a topic we do not route never arrives at all. The
   handler keeps a defensive `not-subscribed` → `ignored` branch, but the spec case that proved it
   has no transport-level equivalent — it is covered at the handler level and in
   `ecom-messaging/test/consumer/kafka-event-handler.spec.ts` instead.
2. **A reservation that does not exist yet exhausts as `transient-exhausted`.** `cat-007`
   dead-lettered a missing hold as `reservation-missing` on the first attempt. That mapping is
   gone: a hold whose transaction has not committed when `order.created` arrives is worth waiting
   for, and rejecting it immediately would turn the normal commit race into a DLQ record.
   `reservation-closed` and `reservation-mismatch` remain mapped, so genuinely terminal states
   still dead-letter on the first attempt.

## The plan's one wrong assumption

The plan said "no migration is needed for cat-008". That was drawn from the tables the import
writes — `processed_events` exists (`006`), `'import'` is already a legal
`stock_movements.reason` (`001`) — and it missed `products_source_check` in `001`, which
enumerated only the platform syncs. `db/008-product-import-source.sql` is therefore a real (if
tiny) migration and the only schema change in the task; writing `'local'` for imported rows would
have made a feed row indistinguishable from one an admin typed in.

## Verification

| Check | Result |
|---|---|
| `catalog-svc` `pnpm test` | 137 passed (22 files) |
| `catalog-svc` `product-imported.handler.spec.ts` | 10 cases: create vs update, preserved columns, category/brand by id and by name, all four conflict reasons, the clamp, no-outbox |
| `catalog-svc` `catalog-consumer.controller.spec.ts` | 15 cases: both topics on one controller, both `translateError` reasons, DLQ-failure ⇒ no commit + throw |
| `catalog-svc` `test/product-imported.e2e-spec.ts` | 14 cases: product + 2 variants + 3 images + 1 `processed_events` row and **zero** `catalog.outbox` rows; a replay writes nothing; a dangling `categoryId` → `product.imported.dlq` with `unresolved-reference`; reserve 2 then import 10 ⇒ on-hand 8 and one `import` movement; the clamp |
| `catalog-svc` `test/order-created.e2e-spec.ts` | unchanged and green — the transport swap changed no reservation behaviour |
| `catalog-svc` `pnpm test:e2e` | 112 passed (12 files) |
| `catalog-svc` `pnpm test:e2e` with `RUN_KAFKA_E2E=1 -- live-kafka.consumer` | 3 passed in 16.7 s: a committed hold from `order.created`, an import with `variants[]` on the wire (products 1.9.0 parses it), and `describeGroups` showing `catalog-svc` `Stable` / `catalog-svc-server` `Dead` |
| `catalog-svc` `pnpm lint` | 0 warnings, 0 errors (128 files) |
| `catalog-svc` `npx tsc --noEmit` | exit 0 |
| `catalog-svc` `nest build` | clean |
| `ecom-infra` `pnpm topics:smoke` | 28/28, including `product.imported.dlq` present with 1 partition |
| `kafka-consumer-groups --list` | exactly `cart-svc`, `catalog-svc`, `search-svc`; no `-server` group |
| `kafka-consumer-groups --describe --group catalog-svc` | `product.imported` p0 offset 1 lag 0, `order.created` p1 offset 3 lag 0 |
| commit | `catalog-svc` `9cd6948` (19 paths) |

## Open

- `catalog-svc-server` must stay dead. The proof above is `describeGroups` state, not a log line:
  a `-server` group with offsets would mean two groups splitting partitions and neither seeing
  every record.
- `order.status.updated` (release stock on cancel/refund) is `cat-010` — one more `@EventPattern`
  on this same controller, never a second strategy.
- An import cannot express a discount window: `effectivePrice` in the payload is ignored and
  catalog derives it from `catalog.product_discounts`.
- `db/008` is the only migration; there is no `cat-008` table to hunt for. Stated here because
  the plan said the opposite.
