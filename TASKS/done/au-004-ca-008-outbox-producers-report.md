# au-004 + ca-008 — transactional outbox producers: final report

> Tasks: `au-004` (auth-svc produces `user.registered`) and `ca-008` (cart-svc produces
> `cart.updated`, `NoopEventBus` deleted). Written after every gate passed on 2026-10-30.
> Read this with `TASKS/done/au-004-auth-outbox-producer.md` and
> `TASKS/done/ca-008-cart-outbox-producer.md`; those carry the file-by-file detail.

## 0. What shipped, in one paragraph

A new package `@ecom/messaging` 0.1.0 owns the envelope builder, the Postgres outbox store,
the relay, and the Kafka publisher, with a Nest factory behind a `./nest` subpath.
`auth.outbox` and `cart.outbox` are migrations `db/003-*.sql`. Registration writes exactly one
`user.registered` row between `assignUserRole` and `COMMIT`; every committed cart mutation writes
exactly one `cart.updated` row in that mutation's transaction, and `convertActiveCart` became
transactional for the one path that publishes `status: 'converted'`. The relay claims rows with
`FOR UPDATE SKIP LOCKED`, publishes one at a time under a per-schema advisory lock, marks them
published, and parks a row at `failed` after five attempts. `NoopEventBus` and every `EVENT_BUS`
reference are gone; five cart e2e suites now assert on `cart.outbox`. Both services pass a gated
live Kafka proof (`RUN_KAFKA_E2E=1`) and skip it by default.

---

## 1. Architecture decisions and trade-offs

| # | Decision | Why | Rejected | What it costs |
|---|---|---|---|---|
| D1 | One shared `@ecom/messaging` package | The claim SQL, the lease, and the retry ladder are the code that gets a bug; one fix point | Copy `order-svc/outbox/` into each service | A package to version, pack, and pin — plus a `pnpm install --ignore-workspace` habit in every adopter |
| D2 | Framework-free core, Nest in `./nest` | 21 unit tests with no DI container; services add one import + one factory call | `@nestjs/common` in the main entry; a hand-written module per service | Two entry points to keep coherent; a subpath export the services must not mix up |
| D3 | Per-schema outbox (`auth.outbox`, `cart.outbox`) | Each service owns its rows and its lease budget; dev shares one database, production will not | One `messaging.outbox` with a producer column | Two identical DDL files, and the two can drift |
| D4 | Store the finished envelope, not the payload | The relay publishes exactly the committed bytes and re-derives nothing; the contract check fires while the write can still be aborted | Store payload, build envelope at publish time | A row carries a fuller envelope than a pure domain table would; the column is `envelope`, deliberately not `payload` |
| D5 | Validate inside the write transaction (fail closed) | A drifted payload aborts the business write loudly instead of parking a permanently unpublishable row | Validate at publish time; trust TypeScript alone | A future contract tightening blocks registrations until the producer is fixed — a **close call**, see below |
| D6 | `type` + `topic` + `eventType` dual-write, `version: 1`, `idempotencyKey = event_id` | `doc-003` requires 1.x producers to dual-write until 2.0.0; `idempotencyKey = id` means a relay retry re-publishes the *same* key so consumer dedupe still works | A natural key such as `cartId:updatedAt` | Three fields that will be deleted at 2.0.0, and a retry that looks identical to a duplicate to any consumer that ignores the payload |
| D7 | Lease + `SKIP LOCKED` + one session advisory lock | The lease makes a crashed relay recoverable without a reaper; `SKIP LOCKED` stops two workers taking one row; the advisory lock is what preserves per-aggregate order across replicas | Rely on a single replica; claim and publish inside one long transaction | Relay throughput is one batch in flight — a **close call**, see below |
| D8 | Retry identical to the queue side: `attempts+1`, `failed` at 5, `min(2^attempts, 60)s` backoff in `locked_until`, `last_error` ≤500 chars | Parity with SQS `maxReceiveCount = 5` keeps one mental model; a parked row is observable instead of retried forever | Infinite retry; a separate outbox retry policy | A transient broker outage longer than ~31 s of backoff ends with `failed` rows that no one currently alerts on |
| D9 | Sequential publish inside a batch (`for` + `await`) | Ordering is the reason the key exists; parallelism would silently break per-cart order | `Promise.all` over the claimed batch | A batch of 20 costs 20 round trips |
| D10 | The publisher **throws** | A relay that swallows a failure marks a lost message `published`; catalog's `KafkaEventBus` swallows, which is fine for a fire-and-forget bus and fatal here | Reuse `KafkaEventBus` | Every caller must handle a throw; only the relay calls it |
| D11 | `producer({ idempotent: true, maxInFlightRequests: 1 })`, `acks: -1` | A producer-level retry cannot duplicate a record | Default producer settings | Producer init is slower and one in-flight request caps producer throughput |
| D12 | No FK from the outbox to the aggregate | A user or cart can be deleted while its event is still pending, and the relay must still publish it | `REFERENCES auth.users(id) ON DELETE CASCADE` | Cleanup in tests is explicit (`DELETE … WHERE aggregate_id = ANY(...)`), and orphan rows are possible |
| D13 | `cart.updated` carries `status` as the contract enum (`CartStatus`) | The pg row was already cast; this removes an unchecked `string` from the one payload that has an enum | Keep `string` and validate at the edge | A cart status added to the contract forces a cart-svc type change |
| D14 | `convertActiveCart` becomes transactional | The convert path is the only one that publishes `status: 'converted'` with items; a bare `UPDATE` cannot hold the snapshot it reports | Read items after the update | One more transaction on a low-traffic internal route |
| D15 | `0.1.0`, pre-1.0, committed tarball + `file:` pin | Two adopters is not enough evidence to freeze a public surface; `1.0.0` lands with the third adopter (`ord-011`) | `1.0.0` now; a published npm package | Every adopter installs with `pnpm install --ignore-workspace`, and a stale copy in `node_modules/.pnpm` is a real failure mode |

### The two genuinely close calls

**Fail-closed validation (D5).** The alternative is attractive: validate at publish time, keep the
write path fast, and let a bad row sit in the outbox. That is worse in exactly the way that matters.
A payload that fails validation at publish time is a row that can *never* be published — it will
burn five attempts, park at `failed`, and require a human to fix data that the domain already
committed. Validating inside the transaction turns that into a loud 500 on one registration that
rolled back cleanly. The cost is real and accepted: a future contract tightening (say `displayName`
shrinks to 80) would block registrations until the producer is updated. That is a *visible*,
same-day fix; a permanently unpublishable row is not.

**The advisory lock (D7).** `SKIP LOCKED` alone is enough to make the relay *correct* — no row is
claimed twice — but not *ordered*: with two replicas, worker A can claim `t1` and worker B `t2`, and
B can win the race to the broker. That breaks the one promise `cart.updated` makes (per-cart
sequence). The advisory lock buys ordering at the cost of throughput: only one relay publishes at a
time, so the ceiling is one batch in flight no matter how many replicas exist. For a learning
platform at this volume that is the right trade, but it is a trade — the moment publish latency
matters, the answer is per-aggregate locking (hash the aggregate id, not the schema), not removing
the lock.

---

## 2. Learning outcomes

1. **"Publish after commit" is not a weaker guarantee, it is a missing one.** The old cart path
   committed the mutation and then called a bus that logged. There is no retry, no record, and no
   way to answer "did this cart ever emit?". The outbox is not a Kafka convenience — it is the only
   place where the fact of the change and the intent to announce it are the same durable write.
   The corollary is what made the design concrete: **the event must be stored in the same
   transaction, and the relay must re-derive nothing**, because the relay has no access to the
   transaction's state.
2. **`SKIP LOCKED` guarantees mutual exclusion, not order.** It is the correct primitive for
   "many workers, one queue" and the wrong one for "one aggregate's events in sequence". Ordering
   needs a second mechanism (here: a single publisher per schema). Conflating the two is how a
   system ends up with duplicates that are correctly deduped and yet applied out of order.
3. **A lease makes crash recovery implicit.** `locked_until` means a worker that dies mid-publish
   leaves rows claimable again after 30 s, with no reaper process and no `next_attempt_at`
   bookkeeping. The failure mode to watch is the opposite one: a lease shorter than the publish
   timeout means two workers own the same row.
4. **`idempotent: true` on the producer is not consumer dedupe.** It protects against *producer-level*
   retries duplicating a record inside Kafka's session. A crash between `send` and `markPublished`
   still re-publishes, so at-least-once still holds end to end, and `idempotencyKey = event_id` is
   what makes the consumer's `processed_events` insert meaningful.
5. **The key, not the partition count, is the ordering contract.** `cart.updated` has 3 partitions;
   that number only decides *where* a key lands, never that one key stays in order. Keying by
   `cartId` survives the identity change at merge, which is why `9.Testing.md`'s old
   `userId|sessionId` claim was a documentation bug with real consequences.
6. **One strict schema produced two gates at once.** Because `eventEnvelopeSchema.parse` and
   `parseEventPayload` run at write time, every producer call site is checked twice: by TypeScript
   when it compiles, and by Zod when it runs. The type does not survive a hand-written `INSERT`, so
   the SQL `CHECK (envelope->>'type' = event_type)` is a third gate — cheap, and it made "the row
   disagrees with its own envelope" unrepresentable.
7. **Post-commit reads are a data race you can see from the outside.** `cart.service` read items
   after `COMMIT` and then built the payload; a concurrent mutation in between produced an event
   describing a state that never existed. Passing the transaction client into `findItems` fixed the
   payload, and `convertActiveCart` needed a real transaction before it could make the same promise.
8. **The tests are where the design got sharpened.** The advisory-lock test (hold the lock on a
   second connection, expect `skipped` and an untouched row) and the rollback test (duplicate email
   answers 409 *and* leaves zero rows) are the two cases that would have been skipped by a
   "publish and assert" test — and they are the ones that pin the semantics.
9. **Parallel spec files are a shared-state problem, not a flakiness problem.** Five suites assert
   on one `cart.outbox` in parallel against one database, so every assertion and every scoped store
   filters by `aggregate_id`. A live spec that drained the *global* queue published other suites'
   rows to a real broker; scoping the store to the aggregate under test turned an accident into a
   no-op.
10. **Ambient shell state is a test-harness bug.** `RUN_KAFKA_E2E=1` left in a reused terminal made
    a plain `pnpm test:e2e` run the live spec and produce real records; the run still looked green.
    A gate is only as honest as the environment it is run in, and "skipped by default" must be
    verified, not assumed.
11. **Polyrepo + a shared package is a versioning exercise, not a code-move.** `0.1.0` pre-1.0 with
    a committed tarball and a `file:` pin is the contracts pattern reused on purpose; the lesson is
    that the *packaging* discipline (what is in the tarball, how it is pinned, how a stale
    `node_modules` copy is detected) matters as much as the code inside it.

---

## 3. Brainstorming questions for the next phases

1. **Outbox growth vs topic retention.** The topic keeps 7 days; the outbox keeps rows forever.
   Does a `published_at < now() - interval` sweeper belong in `@ecom/messaging`, in each service, or
   nowhere until it hurts? What is the archival target — truncate, or move to a cold table so
   "did this cart emit?" stays answerable?
2. **Per-aggregate serialization beyond one advisory lock.** Hashing the aggregate id into a small
   set of advisory locks would allow parallel relays while keeping per-aggregate order. Is that worth
   the complexity before there is a second replica doing anything?
3. **What do we alert on?** `failed` count, oldest pending age, and a relay lock held longer than a
   batch should take. None of the three has a metric today; which one is the page, and which is a
   dashboard?
4. **Does `cart.abandoned` (anl-002) reuse this relay?** It is produced by analytics from `cart.updated`,
   so it is a different kind of producer — does it get its own outbox table, or is analytics'
   producer allowed to be fire-and-forget because the input is already an event?
5. **Does the convert bridge (`ca-007`) survive `ca-009`?** The plan already says `ca-009` deletes
   `POST /cart/internal/carts/:userId/convert`. What replaces the *ordering* guarantee that the
   synchronous call gave checkout, given that `ca-009` is at-least-once and lagging?
6. **Should the `cart.updated` payload shrink?** It carries every item. A large cart approaches the
   1 MB Kafka default, and the payload is the same snapshot on every keystroke-driven quantity
   change. A delta or a "changed item ids" shape would be cheaper but breaks consumers' assumptions;
   which consumers actually need the full snapshot?
7. **When does `@ecom/messaging` earn 1.0.0?** Today's rule is "the third adopter". Is `ord-011`
   enough, or should the package also carry a retention helper and metrics before it is frozen —
   because both would be breaking changes afterwards?
8. **Should catalog/cms migrate?** They still use the in-process `KafkaEventBus` (catalog) or a
   different outbox shape (cms, Mongo). Migrating catalog would delete the last swallow-the-error
   publisher; migrating cms would put two transports inside one relay. Is `@ecom/messaging` the right
   home for a Mongo-backed store, or does that deserve a sibling port?
9. **Is fail-closed validation the right default forever?** At 0.1.0 the producer and the contract
   are in the same release train. Once `@ecom/contracts` 2.0.0 tightens a schema and a producer lags
   a deploy, a fail-closed write means an outage. Should `write()` gain a "record but do not publish"
   escape hatch, and who is allowed to flip it?
10. **Where does the `displayName` 120-char truncation belong?** Right now the producer slices
    `first_name + ' ' + last_name` because the columns allow 201. Is that a producer decision, a
    contract decision (widen to 201), or a reason to stop deriving a display name from two name
    columns at all?

---

## 4. Deviations from the plan (and why)

| Planned | What shipped | Why |
|---|---|---|
| `MergeResult` gains `items` | `MergeResult` keeps `cart` + `merged`; the merge service reads the repository's returned item array | The merge path already had both values, and adding a third field duplicated state across two shapes |
| Live specs boot with `DISABLE_OUTBOX_RELAY=false` and drive `relay.start()` by hand | Live specs override `OUTBOX_PUBLISHER` with a real `KafkaEventPublisher` and drive a scoped `drainOnce()` | The factory reads `enabled` once, at module-declaration time, so flipping the env var after import changes nothing; overriding the provider is the only reliable seam |
| 16 package tests (5 + 5 + 6) | **21** (envelope 6, store 7, relay 8) | The extra cases are the ones that pinned behaviour: dual-write disagreement, the lease ordering assertion, and the `attempts 4 → pending / 5 → failed` mapping |
| `cart-security` "no event on rejected mutation" becomes "no outbox row" | There was no such assertion to convert; one was **added** | The old suite never asserted on the bus for that case. The suite is stronger than the plan assumed, not weaker |
| Live specs drain the module relay | Each live spec scopes the store to its own aggregate (`onlyUser` / `onlyCart`, claim limit 200, then filter) | A live spec that claims the global queue publishes other suites' rows to a real broker; this was found by accident and is now structurally impossible |
| Store scoping inside `auth/test/outbox.e2e-spec.ts` filtered after claiming | Same approach in the happy path (`onlyAggregate(store, userId)`) | With five spec files sharing one database, an unscoped drain consumes another suite's attempts |
| Commit per repo, each naming the task id | **No commits at all** | The standing instruction was "implement the plan"; the repo rule is that a commit needs explicit approval. Everything is uncommitted in `auth-svc` (15 paths), `cart-svc` (31), `Documentation` (10) and `state-for-agents` (2) |
| `ecom-messaging` is a peer git repo with a committed tarball | The directory, the tarball, and the tests exist, but there is **no `.git`** | No repo was initialized. `git init` + an initial commit + a remote is a human decision; nothing in the package depends on a remote |

Two smaller notes worth recording: `findItems` now casts `rows as CartItemRow[]` because the query
column list and the row type are not structurally linked (pre-existing, not introduced here), and
`src/logger.ts` (`ConsoleRelayLogger` / `RecordingLogger`) is not in the plan's file list — it exists
so the relay can log without Nest's `Logger` and so tests can assert on its lines.

---

## 5. Evidence

| Gate | Command | Result |
|---|---|---|
| G0 | `docker ps --filter name=ecom-` | six containers, all `Up 14 hours (healthy)`: postgres, redis, mongo, kafka, localstack, mailpit |
| G1 | `ecom-messaging`: `pnpm test` / `typecheck` / `build` / `pack` + `tar -tzf` | 21 passed (3 files); exit 0; exit 0; `ecom-messaging-0.1.0.tgz`; the tarball lists `dist/**` (incl. `dist/nest/index.js`), `package.json`, `README.md`, `CHANGELOG.md`, and **no `src/`** |
| G2 | `auth-svc`: `pnpm install --ignore-workspace`, `pnpm build`, `pnpm lint`, `tsc --noEmit --incremental false` | build clean; lint 0 warnings / 0 errors (58 files); tsc exit 0 |
| G3 | apply `db/003-auth-outbox.sql`; `pnpm test`; `pnpm test:e2e` | 29 passed (10 files); 45 passed + 1 skipped (12 files); schema e2e asserts 8 tables + `idx_outbox_pending`; the 7-case outbox suite green |
| G4 | `cart-svc`: install/build/lint/tsc; apply `db/003-cart-outbox.sql`; `pnpm test`; `pnpm test:e2e` | lint 0/0 (71 files); tsc exit 0; 91 passed (14 files); 96 passed + 1 skipped (11 files); schema e2e asserts 7 tables + `idx_outbox_pending`; 8-case outbox suite green; five rewired suites green |
| G5 | `RUN_KAFKA_E2E=1 pnpm test:e2e` in both services | auth live spec 1/1 passed (`key = userId`, no `email`, row `published`); cart full run 97 passed including the live spec (`key = cartId`, payload equals the stored row, row `published`) |
| G6 | `ecom-infra`: `pnpm verify` / `pnpm topics:smoke` | **31/31** and **28/28**; 22 declared topics; auto-create still off; nothing drifted |
| G7 | tracker validation (`node`, over `tasks.json`) | 128 unique ids, 0 duplicates, 0 cycles; `done 90` / `todo 38` matches `summary`; `byRepo` done-sum 90, total-sum 128; every non-`todo` `log` path resolves on disk; 15 repo entries |
| package resolution | `@ecom/messaging` + `@ecom/contracts` versions inside each service | `0.1.0` and `1.8.0` in both `auth-svc` and `cart-svc` |

Two harness facts that belong in the evidence rather than in a footnote: the services' default
`pnpm test:e2e` now reports **1 skipped file** each (the live spec), which is the proof that the gate
is off by default; and `RUN_KAFKA_E2E` persisted in the reused shell across calls, which is how the
live spec ran inside a plain e2e run earlier in the session. Before trusting any later "default run"
claim, check `$env:RUN_KAFKA_E2E`.

---

## 6. Handoff

- **Nothing was committed.** Six repos have working-tree changes or a new directory, and
  `ecom-messaging` has no `.git` at all. `tasks.json#unpushed` records the exact state.
- **Nothing was pushed, tagged, or published.** `@ecom/messaging` 0.1.0 exists only as a local tarball.
- **The next producer task is `ord-011`**, which makes order-svc the third adopter, turns
  `cat-009`'s consumer from decorative into live, and is the trigger for cutting
  `@ecom/messaging` 1.0.0.
- **The open questions in §3 are not blockers** for `ord-011`; §3.1 (retention) and §3.3 (alerting)
  become blockers the moment a real deployment runs long enough to grow `failed` rows.
