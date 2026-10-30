# STATUS — Done / Now / Next

> Scope: human-readable mirror of `tasks.json`. `tasks.json` is canonical.
> Status: Active | Date: 2026-10-30
> Counts: **128 total = 81 done + 0 in-progress + 47 backlog**
> Truth rule: “core complete” is **not** “feature complete”. Every pending item
> below has a task ID in `tasks.json`; no service is marked 100% while a task
> remains.

---

## 1. Done — verified, with the remaining work named

| Area | What is actually done | Verification | Still pending |
|---|---|---|---|
| `@ecom/contracts` | 1.7.0 package shipped locally: canonical event envelope with dual-read/write; six event payload schemas + an 11-topic registry with `parseEventEnvelope`/`parseEventPayload`/`dlqTopicName`; media `visibility`; CMS/blog/media/theme/navigation/search schemas; exact tarball distribution. Pins: **catalog-svc, cms-svc and search-svc 1.7.0**; auth-svc, cart-svc and order-svc do not depend on it; storefront/admin unpinned | 88 tests, typecheck, build, local pack green | SQS job schemas; 2.0.0 cutover; release tags (`ec-003..ec-005`) |
| `auth-svc` | 10 core slices; JWT issuer/audience; shared error envelope; service-key internal routes | 29 unit + 37 e2e green | `user.registered` is not published; no outbox; no internal email lookup for notify (`au-004`, `au-005`) |
| `cart-svc` | 6 slices; guest/user cart; wishlist; merge-on-login; TTL; **service-key-guarded `POST /cart/internal/carts/:userId/convert`** (Phase-0 bridge, items preserved, publishes one `cart.updated`, 204 on replay) | 91 unit + 87 e2e green, lint 0, build clean | `NoopEventBus` drops `cart.updated`; fixture catalog; no `order.created` consumer; the conversion bridge is temporary (`ca-008..ca-010`) |
| `catalog-svc` | 7 phases; product/category CRUD; inventory; **persisted idempotent stock reservations** (`db/003`, `src/stock`, expiry sweep); public caching; hardening | 89 unit + 75 e2e green, lint 0, build clean; live checkout decremented stock exactly once | No Kafka consumer; best-effort producer; no `sku` backfill for historical order items (`cat-007..cat-011`) |
| `order-svc` | 7 phases; checkout on the **real catalog contract** (quantity, discriminated result, 409/502/503), `orders.stock_reservation_id`, order lifecycle; **user-scoped, DB-backed idempotency** (`db/004`); **pending-first payment saga** with compensation and resumption; hold released when an order is cancelled or fails; **refunds through the provider with a ledger** (`db/005`) and one canonical `order.status.updated`; service-key routes | 81 unit + 76 e2e green (1 live case skipped), lint 0, build clean; the capture sees a persisted `pending` order, a decline or a lost `TX2` is compensated, a retry resumes instead of duplicating, and a refund is the provider's answer (replay never charges twice) | The hold is committed only by `cat-009`, so a completed order's hold is released by the expiry sweep; outbox only logs; the cart conversion bridge is temporary and best-effort; no sweeper for stale pending payments or stuck refunds; partial refunds unsupported (`ord-011`, `ord-012`) |
| `cms-svc` | Phase 1 + 2; pages/sections/blogs/media/theme; admin API; public cache; **media containment + visibility** (`cms-003`: one checked path builder, realpath re-check, public route 404s private and orphan files, admin ObjectId file route, `public, max-age=60, must-revalidate`); **upload containment** (`cms-004`: `Content-Length` guard before the body, multer limits, magic-byte sniff as the authority with `MEDIA_TYPE_MISMATCH` on a lying header, storage root proven writable at boot) | 133 unit + 75 e2e green, lint 0 (90 files), build clean | `cms.updated` publishes on `cms.events`; no `cms_outbox`; Kafka `media.tasks` (`cms-005..cms-007`) |
| `search-svc` | 7 slices; index/query; Kafka consumer; internal batch endpoint; **event classification + DLQ** (`srch-001`: `invalid-json`/`invalid-envelope`/`invalid-payload` dead-lettered on the first attempt, infra errors keep the 5-attempt ladder, offset committed only after the DLQ write) and **`processed_events` dedupe** in the same transaction as the upsert, with counters on `GET /search/internal/consumer-stats`; contracts 1.7.0 | 117 unit + 92 e2e green, lint 0 (69 files), build clean | No Kafka backfill/replay (`srch-003`); raw kafkajs rather than the Nest transport (`srch-002`); `processed_events` has no retention sweep |
| `storefront-ui` | 14 UI primitives; auth composed blocks and routes; CMS theme/settings; navbar/search; style contracts; ProductCard with 5 variants, aspect ratios, blend modes, independent radii, and /components showcase | 50 test files, 319 tests green, tsc clean, build clean | Commerce routes/components; thin auth client; CMS source wiring; `/api/track`; `/api/revalidate`; contract pin (`sf-049..sf-053`) |
| `Documentation` | Architecture/API/schema/testing/versioning; `auth/cart/cms/order/search` service specs; **transport claims corrected** in `1.Architecture.md`, `2.Tech-Stack.md`, and `state-for-agents/ARCHITECTURE.md` (`doc-001`): 11-topic registry linked to `tasks.json`, browser → `Next /api/track` → `analytics-svc` → Kafka, one consumer group per service, CMS has no Kafka consumer, three SQS queues, `user.registered` carries no `email` | plan regex over the three files → 0 hits; §6.3 has 11 topic rows and `page.viewed` belongs to `analytics-svc`; both repos committed clean | Testing matrix; 1.3.0/2.0.0 release train; notify/analytics/import specs (`doc-002..doc-004`) |

**Not created yet:** `notify-svc`, `analytics-svc`, `import-svc`, `ecom-infra`, `admin-app` (empty). Their work is fully specified as tasks, not claimed as done.

---

## 2. P0 — must finish before “feature complete”

These are the defects that make the current happy path fail or lose money/data.

1. **`cat-009`** — commit the hold from `order.created`. Until it lands, a *paid* order's hold expires after 900s and the stock is restored, i.e. the item can be sold twice. This is now the highest-risk open item.
2. **`ord-012`** — retire the Phase-0 bridge `ca-007` put in place; rely on `order.created`.
3. ~~**`cms-004`** — upload hardening: the size limit is checked after the whole file is buffered, the MIME type is the client's header, and `STORAGE_LOCAL_DIR` is not validated at boot.~~ *(closed 2026-10-30)*
4. ~~**`srch-001`** — malformed/invalid events go to DLQ; unknown types commit with a metric; `processed_events`.~~ *(closed 2026-10-30)*
5. ~~**`sf-048`** — resolve the dirty storefront worktree before commerce work.~~ *(resolved 2026-10-30; ProductCard sf-039 completed)*

---

## 3. Plan after P0

| Phase | Name | Tasks | Exit criterion |
|---|---|---|---|
| P0 | Correctness gate | 14 | Checkout, stock, refunds, media, search DLQ, and docs are correct |
| P1 | Contracts + local harness | 6 | 1.3.0 dual-read; Kafka/Redis/Postgres/Mongo RS/LocalStack/Mailpit up; topics + DLQs provisioned |
| P2 | Producers + storefront seams | 10 | auth/cart/catalog/order/CMS publish only through outboxes; storefront seams live |
| P3 | Consumers + idempotency | 9 | cart/catalog/search/notify/analytics consumers pass duplicate/malformed/DLQ tests |
| P4 | Missing services | 14 | notify, analytics, import own their transports and specs |
| P5 | Integration + deploy | 6 | end-to-end + failure injection green; contracts 2.0.0; CI/observability |
| P6 | Admin app | 1 | scope decision; scaffold only if merchant UI is required |

---

## 4. Messaging ownership (canonical)

**Kafka = domain events only. SQS = task jobs only. HTTP = synchronous reads/writes.**

| Service | Publishes (Kafka) | Consumes (Kafka) | SQS tasks | Must not |
|---|---|---|---|---|
| `auth-svc` | `user.registered` (key `userId`) | — | — | No consumer; no tasks |
| `cart-svc` | `cart.updated` (key `cartId`) | `order.created` | — | No tasks |
| `catalog-svc` | `product.updated` (key `productId`), `category.updated` (key `categoryId`) | `product.imported`, `order.created`, `order.status.updated` | — | No tasks |
| `order-svc` | `order.created`, `order.status.updated` (key `orderId`) | — | — | No consumer; no tasks |
| `cms-svc` | `cms.updated`, `blog.updated` (key `blogId`) | — | `media.resize-image` | No Kafka consumer; no `media.tasks` |
| `search-svc` | — | `product.imported`, `product.updated`, `category.updated`, `blog.updated` | — | No producer; no Kafka backfill |
| `notify-svc` | — | `order.created`, `cart.abandoned`, `user.registered`, `order.status.updated` | `notify.send-email` | No Kafka producer |
| `analytics-svc` | `page.viewed` (key `sessionId`), `cart.abandoned` (key `userId`) | `cart.updated`, `order.created`, `page.viewed`, `user.registered` | — | No tasks; no `reminder.dispatch` |
| `import-svc` | `product.imported` (key `productId`) | — | `import.process-row` | No Kafka consumer |
| `storefront-ui` | — | — | — | No Kafka credentials/client; HTTP only |
| `admin-app` | — | — | — | No direct Kafka/SQS; HTTP only |
| `ecom-infra` | — | — | provisions the three queues | No producer/consumer |
| `@ecom/contracts` | — | — | — | No runtime transport; schemas only |

**Delivery rules:** at-least-once; manual commit after the side effect and
`processed_events` insert commit together; one consumer group per service
(`postfixId: ''`); five retries with 1/2/4/8/16s backoff; every source topic has
a `.dlq` twin; malformed JSON and invalid known payloads go directly to the
DLQ; unknown event types are ignored and committed with a metric.

**Producer rules:** request handlers never publish directly. auth/cart/catalog/
order write a Postgres outbox in the same transaction as the domain change; CMS
writes `cms_outbox` in a Mongo transaction (replica set required). Relays use
`FOR UPDATE SKIP LOCKED`, mark published only after broker ack, retry with
`next_attempt_at`, and dead-letter after five attempts.

---

## 5. Non-Kafka boundaries

- **SQS only:** `notify.send-email`, `import.process-row`, `media.resize-image`. Tasks never go to Kafka.
- **Storefront page views:** `sendBeacon` → Next `/api/track` → `analytics-svc` HTTP → Kafka. The browser/storefront never holds Kafka credentials.
- **Storefront CMS cache:** CMS calls Next `/api/revalidate` over HTTP with a shared secret. No storefront Kafka consumer.
- **Admin:** API/HTTP only.
- **Search backfill/tests:** internal batch HTTP endpoint; Kafka replay is not the backfill mechanism.
- **Cart conversion:** `order.created` event; `ca-007` is a temporary HTTP bridge only.
- **Synchronous reads:** internal REST (catalog snapshots, auth email lookup, order lookup).
- **Dropped:** `reminder.dispatch` (replaced by `cart.abandoned` + `notify.send-email`), `order.refunded` (replaced by `order.status.updated {to:"refunded"}`), `media.tasks` (SQS instead), SNS→SQS event transport.

---

## 6. Pending by repo

| Repo | Total | Done | In progress | Backlog | Next up |
|---|---:|---:|---:|---:|---|
| `storefront-ui` | 53 | 48 | 0 | 5 | `sf-049`, `sf-050`, `sf-051`, `sf-052`, `sf-053` |
| `ecom-contracts` | 5 | 2 | 0 | 3 | `ec-003`, `ec-004`, `ec-005` |
| `auth-svc` | 4 | 2 | 0 | 2 | `au-004`, `au-005` |
| `cart-svc` | 10 | 7 | 0 | 3 | `ca-008`, `ca-009`, `ca-010` |
| `catalog-svc` | 11 | 6 | 0 | 5 | `cat-007`, `cat-008`, `cat-009`, `cat-010`, `cat-011` |
| `order-svc` | 12 | 10 | 0 | 2 | `ord-011`, `ord-012` |
| `cms-svc` | 7 | 4 | 0 | 3 | `cms-005`, `cms-006`, `cms-007` |
| `search-svc` | 3 | 1 | 0 | 2 | `srch-002`, `srch-003` |
| `notify-svc` | 4 | 0 | 0 | 4 | `ntf-001..ntf-004` |
| `analytics-svc` | 4 | 0 | 0 | 4 | `anl-001..anl-004` |
| `import-svc` | 3 | 0 | 0 | 3 | `imp-001..imp-003` |
| `ecom-infra` | 7 | 0 | 0 | 7 | `inf-001..inf-005`, `tst-001`, `tst-002` |
| `Documentation` | 4 | 1 | 0 | 3 | `doc-002`, `doc-003`, `doc-004` |
| `admin-app` | 1 | 0 | 0 | 1 | `adm-001` (deferred) |

> Historical note: counts are tracker entries, not historical slices. `auth-svc`
> `au-001` and `search-svc` slices 0–6 are recorded in repo notes, not as
> separate entries. New work is always a task entry.

---

## 7. Now / Next

- **Now:** `cms-004` and `srch-001` are closed — uploads are bounded before the body and the type comes from the bytes; the search consumer dead-letters what it cannot map and dedupes on event id inside the upsert transaction. Both followed the one-commit-per-file rule and neither was pushed.
- **Next:** `cat-009` (commit the hold from `order.created`) — it is the highest-risk open item: a paid order's hold currently expires after 900s and the stock is restored. `ord-012` retires the bridge that `cat-009` makes unnecessary, so they are best done back to back. Search stays at `srch-002`/`srch-003`, and `srch-003` must decide the replay-versus-dedupe question before anyone replays the log. Do not start `sf-049`+ or `adm-001`.
- **Do not** push, tag, release, or publish packages without explicit approval.
- **Commit style:** one commit per edit/feature, conventional message, author `Dharmil Gajjar <foreafcbeta@gmail.com>`.

---

## 8. Truth checks (2026-10-30)

- `tasks.json` parses; **128 unique IDs**; **0 dependency cycles**; no missing dependencies.
- Every `done`/`in-progress` entry has an existing log under the matching folder; the validator that checks ids, dependency cycles, per-repo counts, and the counts line above returns clean (it found and fixed `ec-002`'s log, which still pointed at `TASKS/in-progress/`).
- Phase coverage: **P0 14, P1 6, P2 10, P3 9, P4 14, P5 6, P6 1 = 60**.
- Repo messaging matches `producesConsumes`; the topic catalog matches repo ownership.
- Unpushed state is exact in `tasks.json#unpushed` (recomputed with `git log @{u}..HEAD`, oldest → newest): **search-svc 7** (`7cdc505..8457867`), **Documentation 3** (`055e585..8a8fbfb`), **state-for-agents 27** through `2443c75` — the commit that carries this line is the 28th and cannot name itself, so recompute before any handoff. Every other repo is level against its upstream and `storefront-ui` is clean (`sf-048` closed).
- `cms-svc` after `cms-004`: 133 unit + 75 e2e green, lint 0 (90 files), build clean, against contracts 1.5.0; an 11 MB attach answers `413 MEDIA_TOO_LARGE` with no body buffered, `this is plainly not a png` declared `image/png` answers `400 MEDIA_TYPE_UNSUPPORTED`, PNG bytes named `.jpg` answer `400 MEDIA_TYPE_MISMATCH`, a real 45-byte PNG is stored as `.png` with `sizeBytes: 45`, and a relative `STORAGE_LOCAL_DIR` aborts boot.
- `search-svc` after `srch-001`: 117 unit + 92 e2e green (was 16/98), lint 0 (69 files), build clean, contracts 1.7.0; the dedupe e2e redelivers one event id with a **newer** timestamp and a different title and still reports `duplicate` while the row keeps "First Delivery", so the stale guard is not what makes it pass; a malformed body lands in `<topic>.dlq` as `invalid-json` and only then commits; an invalid payload is not retried; a failed DLQ write leaves the offset uncommitted and leaves `invalid`/`dlq` at zero; `db/003` is applied to `ecom` and `ecom_search_test`.
- `search-svc` repin `@ecom/contracts` 1.2.0 → 1.7.0 changed exactly 7 lines in `pnpm-lock.yaml` (contracts entries and one integrity hash). `pnpm install` alone reported "Already up to date" while `node_modules` stayed at 1.2.0 — pnpm resolves the workspace from the repo root even when `pnpm-workspace.yaml` excludes this package, so the lockfile needs `--lockfile-only --ignore-workspace --force`.
- `doc-001` after the pass: the plan regex (`SNS\s*(→|->)\s*SQS|SnsSqsBus|SNS fan-out|TRANSPORT=|reminder\.dispatch|per \(service, topic\)|storefront.{0,40}Kafka`) returns 0 hits across the three files; §6.3 has 11 topic rows with `cart.updated` keyed by `cartId`; `cms.updated` has no consumer and `page.viewed` is produced by `analytics-svc`; §7.7 has no `email`; one commit per file (`Documentation` `d02aa48`, `10e38de`; `state-for-agents` `159e8eb`).
- `@ecom/contracts` 1.5.0: 88 tests, typecheck, build, and local pack green (`ecom-contracts-1.5.0.tgz` committed, `*.tgz` force-added); `mediaVisibilitySchema` is optional on `mediaSchema`, so every 1.4.0 payload still parses, and `mediaSchema` is parsed only in the contracts tests, so the field breaks no pinned consumer. No tag or publish.
- `cart-svc` after `ca-007`: 91 unit + 87 e2e green, lint 0, build clean; the removed `DELETE /api/v1/cart/internal/carts/:userId` still answers 404, a missing or wrong `x-service-key` answers 401 `SERVICE_KEY_INVALID`, a user without a cart and a replay both answer 204, a conversion leaves `status='converted'` with its lines intact and exactly one `cart.updated`, and `NODE_ENV=production` refuses to boot on the dev key.
- `order-svc` after `ca-007`: 81 unit + 76 e2e green (1 skipped), lint 0, build clean; `CartClient` posts to the conversion endpoint with `x-service-key`, a 204 is silent, a 404 warns without throwing, and a confirmation never fails on a cart error.
- `cms-svc` after `cms-003`: 115 unit + 70 e2e green, lint 0 (83 files), build clean, against contracts 1.5.0; seven HTTP traversal vectors and eleven key shapes answer `404 MEDIA_NOT_FOUND / File not found` with no `storage`, `media/`, `\` or temp path in the body; a file with no `cms_media` row is 404; a private upload is 404 on the public route and 200 on the admin route with `private, no-store`; the admin route is 401 anonymous and 403 for a customer and 404 for a non-ObjectId id; the public route sends `public, max-age=60, must-revalidate` and `nosniff`; `media.e2e-spec.ts` passes unchanged.
- `cms-svc` repin `@ecom/contracts` 1.1.0 → 1.5.0 surfaced exactly one type error (`blogs.service.ts` `deleted.toObject()` cast), fixed in the same commit.
- `catalog-svc` after `cat-006`: 89 unit + 75 e2e green, lint 0, build clean; `catalog` schema has 14 tables.
- `order-svc` after `ord-008`: 61 unit + 67 e2e green (1 live case skipped), lint 0, build clean; `order.orders` has `idempotency_key`, `idempotency_body_hash` and `idx_orders_idem` (`UNIQUE (user_id, idempotency_key) WHERE idempotency_key IS NOT NULL`).
- `order-svc` after `ord-009`: 70 unit + 71 e2e green (1 live case skipped), lint 0, build clean; the e2e provider reads the order row at capture time and finds it `pending`/`pending`; a decline leaves `failed`/`failed` with no outbox row; a forced `TX2` failure refunds the capture once and closes the order as `failed`/`refunded`; a transient capture error keeps the hold and the same key resumes to 201 with one order, one reservation and one `order.created`.
- `order-svc` after `ord-010`: 77 unit + 76 e2e green (1 live case skipped), lint 0 (70 files), build exit 0; the e2e refund calls the provider once with the stored `transaction_id`, a replay calls it zero times, a provider refusal leaves `refunds.status='failed'` with the order still `delivered` and the payment still `captured`, a retry reuses the ledger row and its reserved amount, and no `order.refunded` row is written; `order.refunds` exists with `UNIQUE (order_id)` and `idx_refunds_order`.
- Two customers sending the same `x-idempotency-key` get two independent orders; concurrent duplicates write exactly one; a second app with a throwing `RedisService` returns 503 `IDEMPOTENCY_UNAVAILABLE` and writes nothing.
- Live reservation replay (catalog on `:4020`): same `reservationId` twice → 201 both times, stock 10 → 8, exactly one `sale` movement; release twice → stock 10, second call `items: []`; release after commit → 409 `RESERVATION_CLOSED`.
- No push, tag, release, or package publish was performed.
