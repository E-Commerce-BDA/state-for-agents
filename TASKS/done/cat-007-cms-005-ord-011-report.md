# P2 producers, wave 2 — cat-007, cms-005, ord-011

> Tasks: `cat-007` (catalog-svc produces `product.updated` / `category.updated`),
> `cms-005` (cms-svc produces `cms.updated` / `blog.updated` from a Mongo transaction) and
> `ord-011` (order-svc's outbox actually publishes). Written after every gate passed on
> 2026-10-31. Read with `TASKS/done/cat-007-catalog-outbox.md`,
> `TASKS/done/cms-005-cms-mongo-outbox.md` and `TASKS/done/ord-011-order-outbox-relay.md`;
> those carry the file-by-file detail, and
> `TASKS/done/au-004-ca-008-outbox-producers-report.md` carries the wave-1 reasoning this
> wave builds on.

## 0. What shipped

`@ecom/messaging` went to **0.2.0** and stopped being a Postgres package: one store port
(`OutboxStorePort<Ctx = Queryable>`) now has two implementations — `PostgresOutboxStore`, which
finally quotes its identifiers, and a new `MongoOutboxStore` — behind the same `OutboxRelay`,
the same envelope builder and the same publisher. All five producers were repinned in the same
pass, because two package versions in one monorepo is how a stale `file:` tarball happens.

On top of that, three services stopped pretending to produce:

| Service | Store | What it publishes now | Written where |
|---|---|---|---|
| catalog-svc | `catalog.outbox` (Postgres, migration `007`) | `product.updated` (key `productId`), `category.updated` (key `categoryId`) | in `withTransaction`, with the client that did the write; payload built and contract-validated by `CatalogOutbox` |
| order-svc | `order.outbox` (Postgres, migration `006`) | `order.created` (key `orderId`), `order.status.updated` (key `orderId`) | in `confirmOrder` after capture, in `updateStatusWithHistory`, and in `refund` |
| cms-svc | `cms_outbox` (Mongo, indexes created at boot) | `cms.updated` (key = page/section/blog key), `blog.updated` (key `blogId`) | in one `session.withTransaction` covering the document write, the revision bump and the outbox insert; cache invalidated after commit |

`catalog.outbox` did not exist before; `order.outbox` existed but stored a bare `payload` and
could not even be addressed, because `order` is a reserved word and the package interpolated
`${schema}.${table}` unquoted; `cms_outbox` did not exist and CMS had no transaction anywhere.
The three producer paths that could silently lose an event are gone: catalog's `KafkaEventBus` /
`EventsService`, order's `OutboxService.dispatchEvent` (which logged and then marked the row
published), and cms's direct `cms.events` publish.

**Contract of each event** (all envelopes canonical 1.8.0: `id`, `type` = topic, `version` 1,
`timestamp`, `producer`, `idempotencyKey` = `id`, `payload`):

- `product.updated` — `{ productId, sku, name, slug, description?, price, stock, status,
  categoryId?, categorySlug?, brandId?, brandName?, imageUrl?, updatedAt }`, `.strict()`.
- `category.updated` — `{ categoryId, name, slug, isActive, imageUrl?, parentId?, updatedAt }`.
- `order.created` — `{ orderId, orderNumber, userId, grandTotal, itemsCount, reservationId,
  createdAt }`, `.strict()`. `reservationId` is what lets `cat-009` commit the hold instead of
  letting the expiry sweep release it; the payload deliberately carries no item list.
- `order.status.updated` — `{ orderId, orderNumber, from, to, note?, actor?, refundAmount?,
  refundReference?, timestamp }`, `.strict()`; a refund is `to: 'refunded'`, never a separate
  event.
- `cms.updated` — `{ scope, version, pageKey?, key? }`, `.strict()`; `scope` is `pages` /
  `sections` / `navigation` / `settings`, and `version` is the revision that committed.
- `blog.updated` — `{ blogId, slug, status, title?, excerpt?, coverUrl?, publishedAt?,
  updatedAt?, categoryId? }`, `.strict()`.

---

## 1. Architecture decisions

| # | Decision | Why | Rejected | What it costs |
|---|---|---|---|---|
| D1 | One store port, two implementations, sharing `OutboxRelay`, `buildEventEnvelope` and the Kafka publisher | One relay means one set of claim, lease and ordering semantics; the relay is the part with the subtle bugs | A cms-local relay (duplicate claim and backoff logic — the thing the package exists to prevent) | A package that now has to be correct against two very different databases, and two stores to test |
| D2 | `OutboxStorePort<Ctx = Queryable>` with `write(ctx, input)` | Mongo needs a session, Postgres a `Queryable`; the default keeps cart's and auth's call sites source-compatible and keeps the context type as the seam's only type safety | `write(client: unknown)`, which compiles everywhere and checks nothing | Every adopter must be right about what it passes; a wrong context is a runtime error, not a compile error |
| D3 | Quote identifiers in the Postgres store: `"${schema}"."${table}"`; keep the advisory-lock key unquoted | `order.outbox` was a syntax error, so `ord-011` was unreachable without this. Quoting is a no-op for `auth` and `cart`, and the unquoted lock key keeps their lock namespace identical | Backticking `order` inside order-svc, which leaks SQL into a service | A store that now trusts its own quoting; any future identifier with an embedded quote becomes the store's problem |
| D4 | Mongo claim = repeated atomic `findOneAndUpdate`, one document per call, up to `limit` | This is the Mongo analogue of `SKIP LOCKED`: the filter (`status: 'pending'`, lease null-or-expired) plus `$set` is atomic per document, so two replicas cannot claim the same row | `find` + `updateMany({_id: {$in: [...]}})`, which can double-claim between the two round trips | Up to `limit` round trips per drain (20 by default) instead of one |
| D5 | Mongo relay lock = lease document with `findOneAndUpdate(..., {upsert: true})`; a duplicate-key error means "not acquired"; release sets the epoch | Postgres has advisory locks; Mongo has nothing equivalent. A lease with an expiry cannot deadlock a crashed relay | `insertOne` as a mutex, which a crash holds forever | Release is a write, not a disconnect; a clock skew long enough to expire a live lease still double-publishes (as it does in Postgres) |
| D6 | `order.outbox` keeps `payload` (now nullable); new rows write only `envelope`; `CHECK (status <> 'pending' OR envelope IS NOT NULL)` | Already-published rows cannot be given an envelope — the original bytes are the only record — and old rows are audit data, not input. Pending pre-envelope rows are parked at `failed` | `DROP COLUMN payload`, which destroys the only record of what consumers already received | A dead column and a parked `failed` population that an operator will eventually ask about |
| D7 | catalog's producer-side `IEventBus` / `KafkaEventBus` / `EventsService` are deleted; the Kafka **consumer** path is untouched | After cat-007 nothing in catalog publishes through the bus, and a second, unpersisted publish path is exactly the drift the task removes | Keeping the bus "for later" | The consumer-side files had to be lifted out of a module that also held the bus, and two specs died with it |
| D8 | A CMS mutation is one Mongo transaction (document write + revision bump + outbox insert); cache invalidation runs **after** commit | Redis cannot join a Mongo transaction, so there are exactly two orders, and only one of them cannot resurrect stale content | Invalidating inside the transaction, which creates a false cache-miss window | Every converted callback must be re-runnable, because `session.withTransaction` retries |
| D9 | `cms.updated` moves from the transport topic `cms.events` to `cms.updated` | `EVENT_TOPICS` names the topic `cms.updated` and the relay keys on `event_type`, so a `cms.events` row would be parked as an unknown event type | Teaching the relay about transport aliases | Any external producer still writing `cms.events` is now wrong, and nothing warns it |
| D10 | `media.tasks` stays on the direct CMS bus | It is not an `EventTopic` (the registry has 11, none of them `media.tasks`), so the relay would park it; `cms-006` moves it to SQS | Forcing a fake topic into the registry | CMS still has one unpersisted publish path, and it is the one that produces a *task* on the *event* transport |
| D11 | "Expand coverage" = emit `product.updated` on variant, option, image and discount mutations; no payload schema change | They all make a cached product card stale, and the existing payload already carries `images` | Adding `variants`/`discounts` to `productUpdatedPayloadSchema`, which is a contracts release plus a search-svc mapper change | Downstream still cannot see variant-level detail; search re-reads the product |
| D12 | catalog-svc and cms-svc repin `@ecom/contracts` 1.7.0 → 1.8.0 | They build envelopes; 1.8.0's `EventEnvelope` requires `type`, so compiling against it is what forces the canonical shape | Upgrading contracts on order-svc only | Two more services that must track the 2.0.0 train |
| D13 | Package goes 0.2.0 (pre-1.0, breaking allowed) and every one of the five services is repinned in the same pass | Two package versions in one monorepo is how stale `file:` tarballs happen — and it did happen once already (see §2) | Bumping only the consumers that need Mongo | A reinstall in all five services on every package change |

### The two sharpest ones

**The port generic (D2).** The cheap version of this seam is
`write(client: unknown, input: OutboxWriteInput)`; it compiles for every caller, never needs a
package release when a new store appears, and would have saved a day. It is worse for exactly
one reason: the *only* thing that goes wrong at this seam is passing the wrong context — a
`Pool` where a session is expected, or a session where the store wants `query()`. With
`unknown`, that mistake is a runtime error inside the relay's claim path, discovered by an e2e
run, in the one code path that runs on a timer and not during a request. With
`OutboxStorePort<Ctx = Queryable>`, `CmsOutbox` injects `OutboxStorePort<MongoSessionLike>` and
the four Postgres adapters inject `OutboxStorePort` and *cannot* pass a session. The default
parameter is what made this free: `cart`'s `CartOutbox` did not change a single line when the
port became generic, which is why G2 (auth and cart fully green after the repin) is a real
proof rather than a hopeful one.

The cost is real: a third store (say DynamoDB) must express its context as a type the port can
carry, and every store implementation must be checked by hand that it uses the context it
declared. Type safety at the seam does not extend into the store.

**Cache-after-commit (D8).** The instinct is to invalidate the cache as part of "the mutation
happened", i.e. inside the transaction, so the two cannot drift. That instinct is wrong here
because Redis is not in the transaction: its `DEL` takes effect immediately and permanently,
while the Mongo write can still roll back. If the transaction then fails, the cache has been
cleared for a state that never existed — a cache miss re-reads the *old* document and re-caches
it, which is harmless. If the transaction succeeds but the invalidation happened first, a
reader in the gap misses the cache, reads the pre-commit document and re-caches it, and the
cache is now permanently stale with nothing to correct it until the next write.

So the only safe order is: commit, then invalidate. That leaves a window where the cache
briefly serves the previous version — a bounded staleness of milliseconds, which is the trade
this system already accepts everywhere (public CMS reads are `max-age=60,
must-revalidate`). The invariant worth remembering is: **a cache invalidation is only correct
after the thing it invalidates can no longer change.**

---

## 2. Trade-offs accepted

1. **Two stores to maintain.** The package now has two implementations of one interface, and a
   bug in the *shared* relay shows up in both while a bug in a store shows up in one. There is
   no conformance suite that boots both against the same assertions (§4.2), so today the
   "one port" claim rests on review, not on a test.
2. **One package version for five services.** Every `@ecom/messaging` change is a repack plus
   five `pnpm install --ignore-workspace` runs, and a service left behind keeps running the old
   code from its own `node_modules`. This is exactly how the `unwrapDocument` bug was found:
   the package was correct, one service's copy was not.
3. **catalog's repository churn.** `products.repository.ts` gained an optional `client` on
   fourteen methods and its three services were rewritten around `withTransaction`. That is the
   largest diff in this wave, and it is the price of a service that had no transaction at all —
   there was nothing for the outbox write to join.
4. **`payload` is still in `order.outbox`.** Old rows keep their original bytes and new rows
   leave the column null. A future cleanup has to prove every environment has only
   `published`/`failed` rows before dropping it, and nothing enforces that today.
5. **`media.tasks` is still unpersisted.** CMS now has a durable path for domain events and
   still has a fire-and-forget path for the media resize job. That is deliberate (D10) and it is
   a wart: the one publish that can be silently lost is the one that makes a thumbnail.
6. **Aggregate-scoped drains in every e2e.** Because all suites share one database, each outbox
   spec scopes its claim to the aggregate under test. That is more test plumbing per spec, and
   it is the only way the suites can run in parallel without publishing each other's rows.
7. **A second `@ecom/contracts` release was not taken.** Adding `variants`/`discounts` to
   `product.updated` would have made the "expand coverage" half of cat-007 stronger. It is
   deferred rather than rejected (§4.7).

---

## 3. Learning outcomes

1. **Reserved words break identifier interpolation, and the break is invisible until the table
   is real.** `"order"` is a schema in this system and `order` is a SQL keyword, so
   `INSERT INTO order.outbox` is a syntax error — but only at the moment a second statement
   references it, which is why order-svc carried a table it could not actually use and nobody
   noticed. Identifiers that come from configuration must be quoted at the boundary, once, and
   the unquoted form kept only where it is a *key* rather than syntax (the advisory lock).
2. **A second driver tests whether a port is real or Postgres-shaped.** Writing
   `MongoOutboxStore` against the existing interface forced three separate clarifications:
   `write` needed a context type rather than a client, `claimBatch` needed a different
   atomicity primitive, and `tryAcquireRelayLock` needed to return a *release action* rather
   than hold a connection. None of those were visible while only Postgres implemented the port.
   A port with one implementation is a naming convention.
3. **"Expand coverage" is a behaviour claim, not a schema claim.** cat-007 says catalog "gains
   variant and discount coverage". The tempting reading is a richer payload; the correct one is
   that mutations which previously emitted nothing now emit the event they already had a schema
   for. Checking which reading the plan meant *before* touching a contract saved a release.
4. **Deleting a producer path is harder than adding one, because tests assert on it.** The
   outbox path had to be built while the old path still existed (so the suite stayed green),
   then the old path deleted, then ~30 assertions moved from a bus spy to a store double. The
   ordering matters: delete first and you cannot tell a broken test from a missing one.
5. **A driver's return shape is part of your interface, even when you do not type it.**
   `mongodb` ~6.20 strips the `ModifyResult` wrapper on the collection type we declared, so
   `findOneAndUpdate(...).value` was `undefined` and the claim returned nothing. The fix was
   ten lines, but the lesson is larger: a structural `*Like` interface is a promise about the
   driver, and drivers change that promise inside a minor version.
6. **`session.withTransaction` retries your callback, so a callback is not a unit of work you
   own.** Every CMS mutation had to become safe to run twice (append, bump, insert — all
   idempotent in the retry sense). A read-modify-write that computed a value outside the
   transaction would silently recompute it on retry, and nothing in the API tells you.
7. **Two stores, one relay: the shared part is where the semantics live.** The interesting
   invariants — sequential publish, backoff ladder, park at five attempts, mark published only
   after ack — are asserted once in the relay's tests and inherited by both databases. That is
   the payoff for refusing a cms-local relay, and it is only visible after the second store
   exists.
8. **`initialize()` belongs on the port, not in a migration.** Mongo has no migration file
   here; `cms_outbox`'s indexes are created by the store at boot, and the initializer is
   registered **even when the relay is disabled** — otherwise a test-only environment would run
   against an unindexed collection and the claim would slowly become a table scan. Index
   creation is part of the store's contract, not the environment's boot script.
9. **Order is a mechanism, not a promise.** `SKIP LOCKED` and an atomic `findOneAndUpdate`
   guarantee exclusivity; the advisory lock and the lease document guarantee that one relay is
   publishing, which is what keeps per-aggregate order. Neither primitive gives you ordering on
   its own, and both databases need the second mechanism spelled out separately.
10. **A gate is only as strong as its environment.** `DISABLE_OUTBOX_RELAY` is read while the
    module is declared, so a spec that sets it after import changes nothing, and
    `RUN_KAFKA_E2E` persists in a reused shell. The live proofs are therefore *overrides of the
    `OUTBOX_PUBLISHER` provider* (not env flips), each scoped to its own aggregate, and the
    default e2e runs report skipped files as the evidence that they are off.
11. **A "no commit" delivery has a cost that compounds.** Five tasks are now uncommitted in
    seven working trees. The review surface is the diff of everything; there is no per-task
    revert point. The tracker records it, but the tracker cannot substitute for history.

---

## 4. Brainstorming questions for the next phases

1. **Outbox retention, now for four tables and one collection.** `auth`, `cart`, `catalog`,
   `order` and `cms_outbox` all grow for the life of the database while the topics keep 7 days.
   Does the sweeper live in `@ecom/messaging` (one config, four vendors), in each service (each
   owns its rows), or in an operator runbook? And does it *delete* `published` rows, or move
   them to a cold table so "did this order ever emit?" stays answerable?
2. **A conformance test that boots both stores.** The port's value is that both stores behave
   identically. One spec, run twice — once against `PostgresOutboxStore`, once against
   `MongoOutboxStore` — over `write` / claim exclusivity / lease expiry / backoff / park /
   lock contention would turn the claim into a test. It needs a real Postgres and a real Mongo,
   which the package currently refuses to require, so where does that suite live?
3. **Should the Mongo store be a separate package?** `@ecom/messaging` now declares a Mongo
   shape it does not depend on. If a second consumer ever needs only Postgres, the Mongo code
   ships to it for nothing. `@ecom/messaging-mongo` would keep each tarball honest, at the cost
   of two packages to version in lockstep.
4. **How will `ca-009` and `cat-010` actually exercise `order.created` and
   `order.status.updated`?** Both events are now on the broker, and both consumers exist only
   as tasks. The integration test that proves "paid order → hold committed → cart converted →
   status event applied" is `tst-001`, and it is the first place the six producer contracts are
   checked against real consumers rather than a recording publisher.
5. **`payload` in `order.outbox`: when can it go?** The migration parked pre-envelope rows at
   `failed`, so nothing will ever publish them. Dropping the column is therefore safe in *this*
   environment — but the migration has to run in every environment before the `DROP`, and
   there is no migration runner (`ADR 4`: no migrations in v1). Does the second `DROP` wait for
   `inf-004`?
6. **What replaces `media.tasks` on the direct bus, and in what order?** `cms-006` moves it to
   SQS `media-resize-image`. Until then CMS has exactly one non-durable publish. Is there a
   cheap interim: refuse to serve the upload if the job cannot be enqueued, or keep the current
   best-effort behaviour and accept an orphan thumbnail?
7. **Do variants and discounts deserve a payload, or a second event?** `product.updated` is
   `.strict()` and carries the product summary. A price change on a variant is the thing a
   storefront actually needs to react to, and today it produces a product-level event with
   unchanged product-level fields. Is the right shape `variant.updated` (a new topic in the
   registry) or `product.updated` with a `variants` array (a contracts release)?
8. **Is `occurredAt` from the row always right?** Catalog stamps the row's `updated_at`, order
   stamps `payload.createdAt`/`timestamp`, CMS lets the caller pass a date. Three conventions,
   one envelope field. Should `buildEventEnvelope` require the caller to justify the timestamp,
   so that "replay reproduces the original event" is enforced rather than remembered?
9. **What is the page on a producer failure?** Five services now have rows that can go
   `failed`, and none of them has a metric. `failed` count, oldest pending age, and a relay lock
   held longer than a batch are the three candidates; only one of them should page. And the
   Mongo store needs the same three, which means the interface probably needs a `stats()`.
10. **Does the `OutboxInitializer` belong in the relay's lifecycle?** Right now indexes are
    created at boot whether or not the relay runs, which is correct for tests and redundant in
    production (four services create the same partial index shape). If a service ever boots
    against a read-only replica, `initialize()` becomes a startup failure for no reason.
11. **When does `@ecom/messaging` earn 1.0.0?** The wave-1 rule was "the third adopter". There
    are now five, and the package has already taken one breaking change (the generic port) plus
    one silent fix (quoting). Is the freezing condition "a retention helper and metrics exist",
    or "nothing in the next two waves will change the port", and who decides?
12. **Should the relay publish in parallel per aggregate?** The current answer is one publisher
    per store (advisory lock / lease document), so ordering is global and throughput is one
    batch. Hashing the aggregate id into N locks would allow N concurrent relays while keeping
    per-aggregate order. Worth doing before there is a second replica? Almost certainly not —
    but the ceiling is now five producers instead of two, and it is worth writing down.

---

## 5. Evidence

| Gate | Command | Result |
|---|---|---|
| G0 | `docker ps` | six containers, all `Up 15 hours (healthy)`: `ecom-pg`, `ecom-redis`, `ecom-mongo`, `ecom-kafka`, `ecom-localstack`, `ecom-mailpit` |
| G1 | `ecom-messaging`: `typecheck` / `build` / `test` / `pnpm pack` + `tar -tzf` | exit 0 / exit 0 / **39 passed (4 files)** / `ecom-messaging-0.2.0.tgz`; the tarball lists 55 entries including `dist/outbox/mongo-outbox.store.js` and `dist/nest/outbox.module.js`, and **no `src/`** |
| G2 | auth-svc + cart-svc after the 0.2.0 repin: `build`, `lint`, `tsc --noEmit`, `test`, `test:e2e` | auth: exit 0, lint 0/0, tsc 0, **29 unit**, **45 e2e** (12 files). cart: exit 0, lint 0/0, tsc 0, **91 unit**, **96 e2e + 1 skipped**. The proof that the port generic and the quoting changed nothing for the two Postgres adopters that existed before |
| G3 | catalog-svc: `build`, `lint`, `test`, `test:e2e` | exit 0, lint 0/0 (119 files), **125 unit**, **96 e2e + 2 skipped** (the live spec); the outbox suite, the rollback proof and the rewired product/category/badge specs green |
| G4 | order-svc: `build`, `lint`, `test`, `test:e2e` | exit 0, lint 0/0 (71 files), **78 unit**, **82 e2e + 3 skipped**; the outbox suite, the schema spec's direct `"order".outbox` insert, and the reworked checkout spec green |
| G5 | cms-svc: `lint`, `build`, `test`, `test:e2e` | lint 0/0 (96 files), exit 0, **132 unit (20 files)**, **81 e2e + 2 skipped**; the 6-case outbox suite (including the rollback proof) green |
| G6 | `RUN_KAFKA_E2E=1 pnpm test:e2e -- test/live-kafka.e2e-spec.ts` in all three, then `kafka-console-consumer` | catalog **2/2** (`product.updated`, `category.updated`), order **2/2** (`order.created`, `order.status.updated`), cms **2/2** (`cms.updated`, `blog.updated`); then one real record consumed per topic with the expected `producer`, key and payload |
| G7 | `ecom-infra`: `pnpm verify` / `pnpm topics:smoke` | **31/31** and **28/28**; 22 declared topics, auto-create still off, nothing invented by the new producers |
| G8 | tracker validation over `tasks.json` | **128** entries, 128 unique ids, 0 duplicates, 0 missing dependencies; **93 done** + 0 in-progress + **35 backlog** matches `summary`; `byRepo` sums match per-repo entries; every non-`todo` `log` path resolves **and** lives in the matching folder; **P2 is 5/10**. The validator was run inline and deliberately not committed — the checks are the list in this row, so a future pass can reproduce them without adopting a script |
| package resolution | `@ecom/messaging` inside each service's `node_modules` | `0.2.0` in auth, cart, catalog, order and cms (verified by the `unwrapDocument` marker after the second repack) |

Two harness facts that belong in the evidence rather than a footnote. First, the live specs
**override `OUTBOX_PUBLISHER`** with a real `KafkaEventPublisher` instead of flipping
`DISABLE_OUTBOX_RELAY`: the relay's `enabled` flag is read while the module is declared, so an
env flip inside a spec is too late — wave 1 learned this the hard way and this wave inherited the
pattern. Second, the default e2e runs now report 2, 3 and 2 **skipped** files respectively,
which is the proof that the gate is off by default; `RUN_KAFKA_E2E` lives in the shell and
survives across terminal calls, so set it explicitly before claiming a default run.

### Deviations from the plan (and why)

| Planned | What shipped | Why |
|---|---|---|
| `cms-svc` migration for `cms_outbox` | no migration file; `MongoOutboxStore.initialize()` creates the indexes at boot through an always-registered `OutboxInitializer` | Mongo indexes are not DDL an operator applies, and running them at boot means tests and production share one definition. The initializer is registered even when the relay is disabled |
| `MongoCollectionLike.findOneAndUpdate` returns `{ value }` (the plan's assumption) | `unwrapDocument()` accepts both the wrapped and the bare document | `mongodb` ~6.20 resolves the bare-document overload; the package was re-packed and all five services reinstalled |
| Live specs prove the plan's six topics, one per service | two topics per service (`order.status.updated` and `blog.updated` were added) | A live gate that only checks one topic of a two-topic service cannot tell a wiring error from a missing event |
| `catalog-svc` repository: `client?: Queryable` on the mutating methods | also on the read helpers those methods need inside the transaction (`findById` and friends) | A delete path that reads the product after committing would emit a payload describing a row that no longer exists |
| `OrderCreatedWrite` written by `checkout.repository.confirmOrder` | `CreateOrderInput.outbox` also accepts the write (currently passed `null` on the TX1 pending insert) | Keeping the shape on both paths means a future single-transaction checkout does not need a new type; the live path is still TX2, after capture |
| `cms-svc` unit specs assert "no event" on some paths | the same assertions now read a fake `OUTBOX_STORE`, plus one new assertion per mutation site | The old spy could only say "the bus was not called"; a store double can say "no row was written", which is the actual invariant |

---

## 6. Handoff

- **Nothing was committed.** `cat-007`, `ord-011` and `cms-005` were delivered with no commit at
  all, exactly like `au-004`/`ca-008`. The work is uncommitted in `catalog-svc`, `order-svc`,
  `cms-svc`, `ecom-messaging`, `Documentation` and `state-for-agents`.
- **Nothing was pushed, tagged, or published.** `@ecom/messaging` 0.2.0 exists only as a local
  tarball, and `ecom-messaging` still has **no `.git`**.
- **P2 is 5/10.** Remaining: `cat-011` (sku backfill), `ca-010` (cart's `cart.updated` consumer
  follow-up) and `sf-049..sf-051` (storefront seams). The producer half of P2 is done: every
  producer in the system publishes only through an outbox.
- **The next tasks are consumers.** `srch-002` (Nest transport instead of raw kafkajs),
  `cat-008` (`product.imported`), then `ca-009` (which unblocks `ord-012`), then `cat-010` and
  `cms-006`.
- **`tst-001` is the first real end-to-end test** and it can now be written: all six producer
  events reach the broker, so checkout → stock hold → cart conversion → status events can be
  asserted against real consumers instead of a recording publisher.
- **The open questions in §4 are not blockers.** §4.1 (retention) and §4.9 (alerting) become
  blockers the moment a real deployment runs long enough to accumulate `failed` rows; §4.2
  (conformance test) is the cheapest way to keep the two-store claim honest.
