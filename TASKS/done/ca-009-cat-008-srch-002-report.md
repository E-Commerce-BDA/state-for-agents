# ca-009 + cat-008 + srch-002 — the consumer wave: final report

> Tasks: `srch-002` (search-svc moves onto the Nest Kafka transport), `ca-009`
> (cart-svc consumes `order.created` and the HTTP bridge is deleted), `cat-008`
> (catalog-svc consumes `product.imported` and its existing consumer moves to the
> same transport). Written after every gate passed on 2026-11-01.
> Read this with `TASKS/done/srch-002-nest-transport-migration.md`,
> `TASKS/done/ca-009-cart-consumes-order-created.md` and
> `TASKS/done/cat-008-product-imported-consumer.md`; those carry the file-by-file detail.
> The enabling work is `@ecom/contracts` 1.9.0 and `@ecom/messaging` 0.3.0, which have
> no task ids of their own — they are delivery vehicles for these three.

## 0. What shipped, in one paragraph each

**`@ecom/contracts` 1.9.0 — one optional field, and an ordering problem.** `productImportedPayloadSchema`
gained `variants?: VariantRef[]` and `productVariantRefSchema` describes one entry (`.strict()`,
`sku` required, `id` optional so Postgres can mint it, `price` payable, `stock` a non-negative
int). Nothing else changed — `productUpdatedPayloadSchema` deliberately did not get the field.
117 tests in 5 files, typecheck, build and `pnpm pack` green. The reason this is its own release
rather than a footnote is `.strict()`: the payload schema rejects unknown keys, so an added field
is *not* backward compatible in practice and 1.9.0 had to reach both consumers before anything
emitted `variants`.

**`@ecom/messaging` 0.3.0 — the consumer half.** Six modules under `src/consumer/`:
`kafka-event-handler.ts` (`run(ctx, topic, raw, handle)` — parse, retry ladder, dead letter,
counter, manual commit, in that order), `processed-events.store.ts` (the claim as
`INSERT … ON CONFLICT (event_id) DO NOTHING RETURNING` in the caller's transaction),
`dlq.publisher.ts` (`<topic>.dlq` through the same naming function the services already used),
`lag.sampler.ts` (a standalone kafkajs admin client, `fetchTopicOffsets − fetchOffsets`),
`consumer-metrics.ts` (nine counters + commit marks) and `kafka-consumer.strategy.ts`
(`ServerKafka` with `postfixId: ''`, `autoCommit: false`, a string deserializer). 100 tests in
9 files; the tarball carries `dist/consumer/*` and no `src/`.

**`srch-002` — search first, because it is the safest proof.** search-svc had a working,
heavily tested `KafkaEventConsumer` with zero business-logic change needed, so it was the cheapest
place to find out whether the new module behaves like the hand-rolled loop. The class is gone
(324 lines) along with its 289-line spec; four `@EventPattern` methods on one strategy replace it,
the group is exactly `search-svc`, and `IndexerService.handleEvent` (transaction + dedupe) and the
DLQ reasons are untouched. 120 unit (18 files) + 92 e2e (1 skipped) green, lint 0 over 72 files,
and one live case consumes a record on the Nest transport and commits its offset.

**`ca-009` — cart conversion became an event, and the bridge disappeared.** `cart.processed_events`
(migration `004`), an `OrderCreatedHandler` that claims the event id and runs
`convertForOrder(client, userId)` plus the existing `cart.outbox` writer inside that one
transaction, `cart-consumer.controller.ts` on the shared strategy, and the deletion of
`src/internal/` — so `POST /cart/internal/carts/:userId/convert` answers `404` with and without
`x-service-key`. A shopper with no active cart is `ignored` and **committed**; that is a normal
life, not a dead letter. 119 unit (17 files) + 96 e2e (2 skipped) green, lint 0 over 81 files.

**`cat-008` — the import, and the blast radius around it.** `ProductImportedHandler` +
`ProductImportRepository` upsert product/category/brand/variants/images in one transaction,
convert imported stock to on-hand (`max(0, imported − openReserved)`) with one `stock_movements`
row `reason='import'`, and write **no** outbox row. Four new terminal DLQ reasons
(`unresolved-reference`, `sku-conflict`, `slug-conflict`, `variant-sku-conflict`) reach the
handler through `translateError`. At the same time `KafkaOrderConsumer` was deleted and both
topics became `@EventPattern`s on one strategy — with `OrderCreatedHandler` byte-for-byte
untouched, which is what made the money-touching migration reviewable. 137 unit (22 files) +
112 e2e (12 files) green, lint 0 over 128 files, three live cases.

The wave moved **all three consumers onto one protocol** and left `P3` at 4/10, with `cart-svc`
carrying an empty queue for the first time since the repo existed.

---

## 1. Architecture decisions, each with the alternative it rejected

| # | Task | Decision | Alternative rejected | Why the rejection lost |
|---|---|---|---|---|
| D1 | all | The consumer protocol lives in `@ecom/messaging`, not in each service | Copy search's proven `KafkaEventConsumer` into cart and catalog | Three copies of the retry ladder, the DLQ ordering and the commit rule is three places for the same bug — and the copy that drifts is the one nobody reads |
| D2 | all | Every `@EventPattern` declares `@Payload()` + `@Ctx()` | Read the context from the strategy, or skip the decorators because "Nest infers them" | It does not infer them: with no parameter metadata Nest falls back to one PAYLOAD at index 0, the second argument is `undefined`, and every commit throws. Found by reading the installed source before writing a handler |
| D3 | all | One strategy and one group per service, `postfixId: ''`, several routes on it | One consumer per topic (group per topic); leave the default postfix | A group per topic means N commits and N rebalances for one service, and `-server` groups double the group count in `--list` while splitting one service's offsets across two ids |
| D4 | contracts | Add `variants[]` as an optional field and publish 1.9.0, then repin both consumers **before** anything emits it | Emit `variants` and let consumers upgrade when convenient; a separate `product.imported.v2` topic | `.strict()` turns an optional field into a breaking change: an old consumer sees an unknown key and dead-letters a perfectly good record. A v2 topic forks the registry for one field |
| D5 | cat-008 | The import writes **no** outbox row | Re-emit `product.updated` so downstream converges "properly" | search already subscribes to `product.imported`; a 10k-row import would become 10k extra events for zero new information, and the outbox would carry the load of an import it did not cause |
| D6 | cat-008 | Imported stock is written as `max(0, imported − openReserved)` + one `stock_movements` row | Write the imported number straight into `products.stock` | `products.stock` is live on-hand already net of holds, so a blind write resurrects reserved units and can oversell. The movement row is what makes the conversion auditable later |
| D7 | ca-009 | The `processed_events` claim and the conversion commit or roll back together | Claim first, commit, then convert | A crash between the two claims an event that was never applied — the cart silently never converts and no retry can fix it, because the id is already spent |
| D8 | ca-009 | No active cart ⇒ `ignored` and committed | Dead-letter it as `no-active-cart`, or throw so it retries | A shopper who never built a cart is the normal case; retrying it forever stalls the partition, and a DLQ row per checkout would be noise that hides real failures |
| D9 | ca-009 | Delete the HTTP convert route in this task | Keep it behind a flag "for safety" | A second path to convert a cart is a second way to convert it twice, and the flag would live until someone found it. order-svc already treats `404` as non-fatal, which is what makes the deletion landable now |
| D10 | ca-009 | cart stays on contracts **1.8.0** while adopting messaging 0.3.0 | Repin cart to 1.9.0 to satisfy the package's peer floor | cart parses no `product.*` payload, so 1.9.0 adds nothing it can use; pnpm resolves the pair and every suite is green. Recorded as debt, not hidden (`8.Versioning.md` §10, ADR 40) |
| D11 | srch-002 | Migrate search first, before cart or catalog | Start with catalog (the biggest surface) or cart (the newest) | search's consumer had the most behavioural coverage and needed no logic change, so any diff in behaviour would be the module's fault, not the migration's. A failure there is unambiguous |
| D12 | cat-008 | `OrderCreatedHandler` untouched; only the transport around it swaps | Rewrite the consumer and the handler together, since it was being opened anyway | The handler touches stock commits. Mixing "new transport" and "new money logic" in one diff makes a failure impossible to attribute, and its existing spec is the baseline that proves the transport swap changed nothing |
| D13 | all | A failed DLQ write throws `KafkaConsumerStalledError` and stops the loop | Log and commit anyway, so the consumer keeps up | Committing past a record that was never applied and never dead-lettered is a silent data loss with a green dashboard. Stopping is loud, recoverable, and surfaces on `/health` |
| D14 | all | The lag sampler is a standalone admin client, not part of the Nest strategy | Reach into `ServerKafka`'s consumer for its offsets | The strategy's consumer is mid-run and its offsets are the ones just committed; a separate client answers "how far behind is the group" without depending on internal state, and it works while the consumer is stopped |
| D15 | cat-008 | Variants never delete-by-absence on import | Treat the incoming `variants[]` as the complete set, like images | For images the list is the product's presentation and absence really means removed. For variants absence is ambiguous (a partial import, a paginated export) and deleting a variant breaks order history that references it |
| D16 | cat-008 | Images are a replace-set, and the old primary is deleted **before** the new one is inserted | Upsert images, letting `one_primary_per_product` sort itself out | That unique constraint fires mid-transaction on any re-import where the primary changes. Ordering the delete first is the difference between a working import and a 500 on the second run |
| D17 | all | `KAFKA_CONSUMER_ENABLED` (default true, false in tests) guards `startAllMicroservices` | Always start the consumer; let the suites mock it | Every e2e suite would otherwise need a broker or a mocked strategy, and a test run would attach to a real group. The flag parks the consumer without touching the HTTP surface |
| D18 | all | Counters and commit marks live in the package; the endpoint lives in the service | One shared `/consumer-stats` route in the package | Each service mounts its own controller and its own auth/internal prefix; a shared route would have to know three routing conventions. cart simply has not mounted one yet, which is recorded as debt rather than papered over |

### The two genuinely close calls

**No re-emit on import (D5).** The appeal of D5's alternative is real: `product.updated` is the
event every other consumer already understands, and emitting it would mean search never needs to
know about imports. It lost on volume and on ownership. Volume: an import of 10k rows would write
10k outbox rows and publish 10k events to announce a single operator action. Ownership: the import
does not own presentation fields (`photo_settings`, `card_settings`, `attributes`, `tags`), so the
`product.updated` it would emit is a lie about what changed. The accepted cost is that a future
consumer of `product.updated` will not see imports, which is now written down in ADR 36 so nobody
"fixes" it later.

**Physical versus on-hand stock (D6).** The trap is that both numbers are called "stock". The
catalog's `products.stock` is what a shopper can buy right now — reservations already decremented
it. An importer, by contrast, knows what physically exists. Writing the physical number straight
in resurrects every open hold; writing `physical − holds` and clamping at zero is the only formula
that keeps the invariant `onHand + openReserved ≤ physical`. The clamp is the ugly part: a
reservation larger than the new physical count means the shop already oversold, and the honest
response is to set on-hand to 0 and log a warning rather than emit a negative quantity into a
CHECK constraint.

---

## 2. Trade-offs accepted

1. **order-svc logs a `404` per checkout until `ord-012`.** `CartClient` still posts to the deleted
   convert route. It treats `404` as non-fatal, which is exactly why `ca-009` could land before
   `ord-012` — but a warning-per-checkout is noise that will eventually hide a real one.
2. **cart has consumer counters and no `/consumer-stats` route.** search and catalog both expose
   one; cart owns the metrics object and serves nothing. Its group is observable only from
   `kafka-consumer-groups`. Named in `STATUS.md` §7 and in `ca-009`'s follow-ups.
3. **cart runs one contracts floor below the package's peer range** (1.8.0 against `>=1.9.0 <2`).
   Deliberate, resolved by pnpm, green in every suite, documented in `8.Versioning.md` §10.
4. **The retry ladder stalls the partition.** Five attempts over 31 s in-process means a genuinely
   bad record blocks its partition for half a minute before dead-lettering. Accepted since
   `srch-001`; the alternative — commit past a failure — is D13's rejected branch.
5. **`variants[]` exists on `product.imported` and not on `product.updated`.** Asymmetry by design:
   the import needs variant references, the update path did not get them in this wave. Noted in
   `8.Versioning.md` so the next reader sees a decision, not an oversight.
6. **An import cannot express "remove this variant".** Absence is ambiguous (D15), so the only way
   to deactivate one is to send it with `isActive: false`. Nothing documents that at the operator
   level yet, because `import-svc` is still `imp-001..imp-003`.
7. **The import does not re-emit, so a merchant's own tooling sees nothing.** Anything watching
   only `product.updated` misses imports entirely. That is D5's accepted cost, and `cat-011`'s
   fixture-seed guard is the nearest thing to a mitigation.
8. **No `processed_events` retention sweep anywhere.** Three Postgres tables and the outbox are
   growing forever. Recorded as debt in three repos' follow-ups plus `10.Observability.md`.
9. **`unresolved-reference` is replayable only by hand.** The record is in `product.imported.dlq`
   with a reason, and there is no replay command in any repo (`srch-003` will build one for
   search). Re-delivery today means an operator republishing by hand.
10. **The lag sampler polls every 15 s from every replica.** Three services, one sampler each, one
    `fetchOffsets` + `fetchTopicOffsets` pair per tick. Trivial now; it becomes interesting the
    day there are replicas, and nothing aggregates the three answers yet.

---

## 3. Learning outcomes

1. **"Nest infers the parameters" is false, and the failure is silent.** An `@EventPattern` handler
   with no `@Payload()`/`@Ctx()` decorators compiles, runs, indexes documents — and throws on the
   first commit, because the context argument is `undefined`. The consumer looks healthy from the
   outside and never advances. The fix was to read `server-kafka.js` and `rpc-context-creator.js`
   in `node_modules` before writing the handler, not after the first mysterious timeout.
2. **`design:paramtypes` is part of the API surface.** Typing the context parameter `unknown`
   emits `Object`, and `ValidationPipe#toValidate` skips only `String` and `Object` — so the pipe
   leaves the Kafka context alone instead of rebuilding it. A type annotation, not a decorator,
   is what keeps the pipe out of the way.
3. **`postfixId` turns a config detail into a data-layout decision.** The default appends `-server`
   to the group id; the group id is where offsets live. Renaming it later re-reads the whole topic
   from the beginning. It is one string and it must be `''` before the first boot.
4. **A strict schema makes an optional field an ordering constraint.** `.strict()` is right for
   payloads — it turns a producer/consumer drift into a loud dead letter instead of an ignored
   field. The consequence is that adding a field has a *rollout order*, and the CHANGELOG has to
   say "repin the consumers first" or the next person ships a breaking change in a MINOR.
5. **Dedupe must share the transaction with the effect.** The claim and the write are one unit
   (D7); split them and the failure mode is silent and permanent — the event id is spent, the
   work never happened, and redelivery is a no-op.
6. **"Normal no-op" and "bad record" are different outcomes and must have different code paths.**
   No active cart, not subscribed, no reservation: all committed, none dead-lettered. A DLQ that
   fills with normal life is a DLQ nobody reads.
7. **A DLQ write failure is the one case where stopping is correct.** Everything else is
   `kind`-based and never throws; committing past a record that was neither applied nor
   dead-lettered is worse than a stopped consumer, because a stopped consumer is visible.
8. **Two numbers called "stock" will eventually be confused.** Physical and on-hand differ by open
   holds; the import is the first writer that only knows the physical one. The formula and the
   clamp now live in one repository method with ADR 37 behind them.
9. **Re-emitting to make a graph "clean" is how a batch becomes a storm.** D5's alternative would
   have converted one operator action into 10k outbox rows. The graph was already clean: search
   subscribes to the source event.
10. **Deleting an endpoint is a client-compatibility question, not a code question.** `ca-007`
    added the bridge, `ca-009` deleted it, and the deletion was safe only because the one caller
    already treats `404` as "cart conversion is best-effort". Twenty lines of existing test is
    what made the deletion a one-commit decision.
11. **Group identity is proved by the broker, not by the config.** `fetchOffsets` does not throw
    for an unknown group — it returns empty, which reads exactly like a healthy brand-new group.
    `describeGroups` (`Stable` vs `Dead`) is the assertion that actually distinguishes "our group
    is running" from "our group name is a typo".
12. **A transport migration with zero behavioural change is the reviewable kind.** `cat-008` moved
    a money-touching consumer and the diff was defensible only because `OrderCreatedHandler` did
    not change at all. Every case the old spec asserted was re-pointed, none was deleted.

---

## 4. Brainstorming questions for the next phases

1. **How long do we tolerate the per-checkout `404` warning?** `ord-012` deletes `CartClient`, but
   until then the log line is correct and useless. Should `CartClient` log `404` at `debug` now
   that the absence is expected — or does that hide the case where checkout really did need the
   conversion?
2. **Should cart get `/consumer-stats` for symmetry, or is the group listing enough?** search and
   catalog serve counters + `lag` + `lastCommit`; cart serves nothing. Symmetry is a controller
   and a spec; the reason to skip it is that nothing scrapes the other two yet either.
3. **What is the replay mechanism for `product.imported.dlq`?** `unresolved-reference` is
   replayable in principle and by-hand in practice. `srch-003` will build replay for search — does
   catalog get one, or is a shared CLI the answer for all three?
4. **Does `cat-010` need a new movement reason?** Releasing stock on cancel/refund will write a
   movement; `'import'`, `'sale'`, `'release'` are the current CHECK values. If the release path
   needs its own reason the CHECK gets a migration, and that migration is the one `cat-008` was
   happy not to need.
5. **What shape is `cat-011`'s fixture-seed guard?** The e2e suites seed reference data; an import
   that creates categories and brands can now collide with that seed. A guard could be a
   deterministic slug namespace, a `source='fixture'` marker, or an assertion in the seed helper.
6. **Who owns `source` after an import meets the admin?** A merchant edits an imported product
   through the admin API: does `source` become `'admin'`, stay `'import'`, or gain a third value?
   Today the import never rewrites `source`, which answers "not the import's business" but not the
   reverse direction.
7. **Does the replace-set image policy destroy curated media on re-import?** It deletes images not
   in the incoming list, which is correct for a full export and destructive for a partial one.
   D15's answer for variants ("absence is ambiguous") argues the same way about images, and the
   reasoning has not been applied there.
8. **Should the three handlers share a conformance suite?** All three sit behind the same
   `KafkaEventHandler`, and all three controllers have their own spec. One shared fake-context
   harness would stop the specs drifting apart as the protocol grows.
9. **Is `product.updated` missing `variants[]` a problem for anyone yet?** Nobody reads variants
   from an update today. `sf-051` (product pages) is the first plausible reader, and it will read
   over HTTP, not Kafka.
10. **When do the lag numbers get aggregated?** Three samplers, three internal endpoints, no
    exporter. `inf-004`/`inf-005` own alarms; the question is whether the answer is a Prometheus
    scrape or an infra-side consumer-group check that never touches the services.
11. **Should `KAFKA_CONSUMER_ENABLED=false` be allowed in production?** It exists for tests. In
    production it means a service that reads a topic and never applies it, with a healthy
    `/health`. Either the flag is refused outside `NODE_ENV=test`, or `/health` reports it.
12. **Does `processed_events` need a per-topic discriminator for retention?** All three tables are
    shaped the same and all three will be swept eventually; a sweep per service is three jobs, and
    a shared helper in `@ecom/messaging` is one more thing in a package that was supposed to be
    feature-complete at 0.3.0.

---

## 5. Gate evidence

| Gate | Command | Result |
|---|---|---|
| G1 | `ecom-contracts`: `pnpm test` / `typecheck` / `build` / `pack` | **117 passed in 5 files**; typecheck exit 0; build clean; `ecom-contracts-1.9.0.tgz` force-added; the tarball lists `dist/schemas/events.*` with the variants schema |
| G2 | `ecom-messaging`: `pnpm test` / `typecheck` / `build` / `pack` | **100 passed in 9 files**; typecheck exit 0; build clean; the tarball lists `dist/consumer/*` (`kafka-event-handler`, `processed-events.store`, `dlq.publisher`, `lag.sampler`, `consumer-metrics`, `kafka-consumer.strategy`) and **no `src/`** |
| G3 | `search-svc`: `pnpm lint` / `test` / `tsc` / `build` / `test:e2e`, then `RUN_KAFKA_E2E=1` | lint **0 warnings / 0 errors** (72 files); **120 passed** (18 files); tsc exit 0; build clean; **92 passed + 1 skipped** (8 files); live run **1 passed** — "indexes a record consumed by the Nest transport and commits its offset" (3588 ms) |
| G4 | `cart-svc`: `pnpm lint` / `test` / `tsc` / `build` / `test:e2e` + live | lint 0 (81 files); **119 passed** (17 files); tsc exit 0; build clean; **96 passed + 2 skipped** (12 files); `order-created.handler.spec.ts` 8 cases, `cart-consumer.controller.spec.ts` 10; `internal.e2e-spec.ts` asserts `404` with and without `x-service-key`; 3 live cases |
| G5 | `catalog-svc`: same, plus `RUN_KAFKA_E2E=1` | lint 0 (128 files); **137 passed** (22 files); tsc exit 0; build clean; **112 passed** (12 files); `test/product-imported.e2e-spec.ts` 14 cases — product + 2 variants + 3 images + 1 `processed_events` row and **0** `catalog.outbox` rows, a replay writes nothing, a dangling `categoryId` → `product.imported.dlq`/`unresolved-reference`, reserve 2 then import 10 ⇒ on-hand 8 and one `import` movement, plus the clamp; `test/order-created.e2e-spec.ts` unchanged and green; live run **3 passed in 16.7 s** including `describeGroups` |
| G6 | `ecom-infra`: `pnpm verify`, `pnpm topics:smoke` | **31/31** and **28/28**, 22 declared topics, auto-create still off. Nothing changed — `order.created.dlq` and `product.imported.dlq` already existed, which is what this gate was for |
| G7 | `docker exec ecom-kafka kafka-consumer-groups --list` | exactly **`cart-svc`, `catalog-svc`, `search-svc`**; no `-server` suffix anywhere. Cross-checked inside catalog's live spec with `describeGroups`: `catalog-svc` `Stable`, `catalog-svc-server` `Dead` |
| G8 | inline `node -e` over `tasks.json` (script not committed) | **128 tasks, 99 done / 0 in-progress / 29 todo**, 0 duplicate ids, `byRepo` equals the entries field by field, `summary` equals the computed totals, every done task's `log` resolves inside `TASKS/done/` and carries `verified: true`, no `todo` carries a log or a `finished` date, `P3` 4/10, `nextUp` = `sf-051`, `cat-011`, `ord-012` |

Two harness facts belong in the evidence rather than a footnote. The e2e runs report skipped files
by default (search 1, cart 2 — catalog's suite reports none, its three live cases are separate) —
those are the `RUN_KAFKA_E2E` live specs, so a "green e2e" claim has to say whether the gate was on,
and this report says it both times. And the `-server` proof is a broker query, not a config read:
`fetchOffsets` returns empty for a group that does not exist, which is indistinguishable from a
healthy new group, so only `describeGroups` can tell "our group is running" from "our group name has
a typo".

---

## 6. Handoff

- **Six commits, one per repo, all local-only.** `ecom-contracts` **`8b4020a`** (1.9.0),
  `ecom-messaging` **`9deff71`** (0.3.0), `search-svc` **`84dea4a`** (22 paths),
  `cart-svc` **`f707431`**, `catalog-svc` **`9cd6948`**, `Documentation` **`081c8d0`** (9 files,
  +366/−67). `state-for-agents` carries this tracker commit, which cannot record its own hash.
- **Nothing was pushed, tagged, released or published.** No package was published anywhere; both
  tarballs are committed files pinned by `file:`. `ecom-messaging` has no remote at all, so its two
  commits cannot leave this machine until a human adds one.
- **`P3` is 4/10** (`ca-009`, `cat-008`, `cat-009`, `srch-002`), `P2` is 8/10. `cart-svc` is at
  10/10 with an empty queue, and `ord-012` is unblocked for the first time.
- **The three debts this wave created, all named rather than implied:** order-svc's `404` per
  checkout until `ord-012`; cart's missing `/consumer-stats` route; cart's contracts floor one
  minor below the package's peer range. None of them is a task in `tasks.json`, and all three are
  in `STATUS.md` §7.
- **Docs moved with the code:** `1.Architecture.md` §6.5, `4.API-Design.md` (the convert route is
  gone), `8.Versioning.md` (1.9.0 row, strict-schema ordering, §10 pin mismatch),
  `9.Testing.md` (two new P0 rows), `10.Observability.md` (lag/commit for all three consumers),
  and `services/{cart,catalog,search}.md` — `catalog.md` is new in this wave.
- **If you inherit this and only read one thing:** `ecom-messaging/src/consumer/kafka-event-handler.ts`
  is the whole protocol in one file, and the comment block on
  `search-svc/src/events/search-consumer.controller.ts` records the `@Payload()`/`@Ctx()` trap
  that costs an afternoon to rediscover. Every other file in the wave is a handler that plugs into
  those two.
