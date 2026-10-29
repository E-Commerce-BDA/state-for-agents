# STATUS — Done / Now / Next

> Scope: human-readable mirror of `tasks.json`. `tasks.json` is canonical.
> Status: Active | Date: 2026-10-30
> Counts: **128 total = 73 done + 1 in-progress + 54 backlog**
> Truth rule: “core complete” is **not** “feature complete”. Every pending item
> below has a task ID in `tasks.json`; no service is marked 100% while a task
> remains.

---

## 1. Done — verified, with the remaining work named

| Area | What is actually done | Verification | Still pending |
|---|---|---|---|
| `@ecom/contracts` | 1.3.0 package: canonical event envelope with dual-read/write; CMS/blog/media/theme/navigation/search schemas; exact tarball distribution; consumer pins still at 1.0.0/1.1.0/1.2.0 | 54 tests, typecheck, build, local pack green | Missing event/job payloads; 2.0.0 cutover; release tags (`ec-002..ec-005`) |
| `auth-svc` | 10 core slices; JWT issuer/audience; shared error envelope; service-key internal routes | 29 unit + 37 e2e green | `user.registered` is not published; no outbox; no internal email lookup for notify (`au-004`, `au-005`) |
| `cart-svc` | 6 slices; guest/user cart; wishlist; merge-on-login; TTL | 84 unit + 79 e2e green | `NoopEventBus` drops `cart.updated`; fixture catalog; no `order.created` consumer; conversion endpoint missing (`ca-007..ca-010`) |
| `catalog-svc` | 7 phases; product/category CRUD; inventory; **persisted idempotent stock reservations** (`db/003`, `src/stock`, expiry sweep); public caching; hardening | 89 unit + 75 e2e green, lint 0, build clean; live checkout decremented stock exactly once | No Kafka consumer; best-effort producer; no `sku` backfill for historical order items (`cat-007..cat-011`) |
| `order-svc` | 7 phases; checkout on the **real catalog contract** (quantity, discriminated result, 409/502/503), `orders.stock_reservation_id`, order lifecycle; **user-scoped, DB-backed idempotency** (`db/004`); **pending-first payment saga** with compensation and resumption; hold released when an order is cancelled or fails; **refunds through the provider with a ledger** (`db/005`) and one canonical `order.status.updated`; service-key routes | 77 unit + 76 e2e green (1 live case skipped), lint 0, build clean; the capture sees a persisted `pending` order, a decline or a lost `TX2` is compensated, a retry resumes instead of duplicating, and a refund is the provider's answer (replay never charges twice) | The hold is committed only by `cat-009`, so a completed order's hold is released by the expiry sweep; outbox only logs; cart clear 404; no sweeper for stale pending payments or stuck refunds; partial refunds unsupported (`ord-011`, `ord-012`) |
| `cms-svc` | Phase 1 + 2; pages/sections/blogs/media/theme; admin API; public cache | 89 unit + 53 e2e green | `cms.updated` publishes on `cms.events`; no `cms_outbox`; Kafka `media.tasks`; traversal-prone media route; post-buffer MIME/size checks (`cms-003..cms-007`) |
| `search-svc` | 7 slices; index/query; Kafka consumer; internal batch endpoint | 97 unit + 85 e2e green | Malformed JSON is committed without DLQ; no `processed_events`; unknown types have no metric; raw kafkajs rather than Nest transport (`srch-001..srch-003`) |
| `storefront-ui` | 14 UI primitives; auth composed blocks and routes; CMS theme/settings; navbar/search; style contracts | suite must be re-established after the dirty worktree is resolved | Commerce routes/components; thin auth client; CMS source wiring; `/api/track`; `/api/revalidate`; contract pin; dirty worktree (`sf-048..sf-053`, `sf-039` in progress) |
| `Documentation` | Architecture/API/schema/testing/versioning; `auth/cart/cms/order/search` service specs | docs exist; transport review pending | Transport contradictions; testing matrix; 1.3.0/2.0.0 release train; notify/analytics/import specs (`doc-001..doc-004`) |

**Not created yet:** `notify-svc`, `analytics-svc`, `import-svc`, `ecom-infra`, `admin-app` (empty). Their work is fully specified as tasks, not claimed as done.

---

## 2. P0 — must finish before “feature complete”

These are the defects that make the current happy path fail or lose money/data.

1. **`ec-002`** — missing payloads (`user.registered`, `cart.updated`, `cart.abandoned`, `order.created`, `order.status.updated`, `page.viewed`). `ec-001` is done: canonical envelope 1.3.0, 54 tests green. `order.created` now carries `reservationId`, which is still undocumented in the package.
2. **`cat-009`** — commit the hold from `order.created`. Until it lands, a *paid* order's hold expires after 900s and the stock is restored, i.e. the item can be sold twice. This is now the highest-risk open item.
3. **`ord-012`** — remove the broken cart HTTP clear; rely on `order.created`.
4. **`ca-007`** — temporary internal cart conversion endpoint (removed when `ca-009` lands).
5. **`cms-003` / `cms-004`** — close media path traversal, unauthenticated file serving, post-buffer MIME/size checks.
6. **`srch-001`** — malformed/invalid events go to DLQ; unknown types commit with a metric; `processed_events`.
7. **`sf-048`** — resolve the dirty storefront worktree before commerce work.
8. **`doc-001`** — remove SNS→SQS, storefront-Kafka, per-topic-group, CMS-consumer, `media.tasks`, `reminder.dispatch`, and `order.refunded` claims.

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
| `storefront-ui` | 53 | 46 | 1 | 6 | `sf-048`, `sf-049`, `sf-050`, `sf-051`, `sf-052`, `sf-053` |
| `ecom-contracts` | 5 | 1 | 0 | 4 | `ec-002`, `ec-003`, `ec-004`, `ec-005` |
| `auth-svc` | 4 | 2 | 0 | 2 | `au-004`, `au-005` |
| `cart-svc` | 10 | 6 | 0 | 4 | `ca-007`, `ca-008`, `ca-009`, `ca-010` |
| `catalog-svc` | 11 | 6 | 0 | 5 | `cat-007`, `cat-008`, `cat-009`, `cat-010`, `cat-011` |
| `order-svc` | 12 | 10 | 0 | 2 | `ord-011`, `ord-012` |
| `cms-svc` | 7 | 2 | 0 | 5 | `cms-003`, `cms-004`, `cms-005`, `cms-006`, `cms-007` |
| `search-svc` | 3 | 0 | 0 | 3 | `srch-001`, `srch-002`, `srch-003` |
| `notify-svc` | 4 | 0 | 0 | 4 | `ntf-001..ntf-004` |
| `analytics-svc` | 4 | 0 | 0 | 4 | `anl-001..anl-004` |
| `import-svc` | 3 | 0 | 0 | 3 | `imp-001..imp-003` |
| `ecom-infra` | 7 | 0 | 0 | 7 | `inf-001..inf-005`, `tst-001`, `tst-002` |
| `Documentation` | 4 | 0 | 0 | 4 | `doc-001..doc-004` |
| `admin-app` | 1 | 0 | 0 | 1 | `adm-001` (deferred) |

> Historical note: counts are tracker entries, not historical slices. `auth-svc`
> `au-001` and `search-svc` slices 0–6 are recorded in repo notes, not as
> separate entries. New work is always a task entry.

---

## 7. Now / Next

- **Now:** `ord-010` is closed — a refund is a ledger row reserved before the provider call and settled after it (one refund per order, `UNIQUE (order_id)`), so a replay never moves money twice and a provider refusal leaves the order and the payment untouched for a retry. `order.refunded` is gone; every status change emits one `order.status.updated {from, to, …}`.
- **Next:** `cat-009` (commit the hold from `order.created`) → `ca-007` → `cms-003`. Do not start `sf-048`+ or `adm-001`.
- **Do not** push, tag, release, or publish packages without explicit approval.
- **Commit style:** one commit per edit/feature, conventional message, author `Dharmil Gajjar <foreafcbeta@gmail.com>`.

---

## 8. Truth checks (2026-10-30)

- `tasks.json` parses; **128 unique IDs**; **0 dependency cycles**; no missing dependencies.
- Every `done`/`in-progress` entry has an existing log under the matching folder.
- Phase coverage: **P0 14, P1 6, P2 10, P3 9, P4 14, P5 6, P6 1 = 60**.
- Repo messaging matches `producesConsumes`; the topic catalog matches repo ownership.
- Repos are level with upstream except `Documentation` (`d0cefcf`) and `ecom-contracts` (`4383b26`). `storefront-ui` is dirty and must be resolved by `sf-048`.
- `@ecom/contracts` 1.3.0: 54 tests, typecheck, build, and local pack green; no tag or publish.
- `catalog-svc` after `cat-006`: 89 unit + 75 e2e green, lint 0, build clean; `catalog` schema has 14 tables.
- `order-svc` after `ord-008`: 61 unit + 67 e2e green (1 live case skipped), lint 0, build clean; `order.orders` has `idempotency_key`, `idempotency_body_hash` and `idx_orders_idem` (`UNIQUE (user_id, idempotency_key) WHERE idempotency_key IS NOT NULL`).
- `order-svc` after `ord-009`: 70 unit + 71 e2e green (1 live case skipped), lint 0, build clean; the e2e provider reads the order row at capture time and finds it `pending`/`pending`; a decline leaves `failed`/`failed` with no outbox row; a forced `TX2` failure refunds the capture once and closes the order as `failed`/`refunded`; a transient capture error keeps the hold and the same key resumes to 201 with one order, one reservation and one `order.created`.
- `order-svc` after `ord-010`: 77 unit + 76 e2e green (1 live case skipped), lint 0 (70 files), build exit 0; the e2e refund calls the provider once with the stored `transaction_id`, a replay calls it zero times, a provider refusal leaves `refunds.status='failed'` with the order still `delivered` and the payment still `captured`, a retry reuses the ledger row and its reserved amount, and no `order.refunded` row is written; `order.refunds` exists with `UNIQUE (order_id)` and `idx_refunds_order`.
- Two customers sending the same `x-idempotency-key` get two independent orders; concurrent duplicates write exactly one; a second app with a throwing `RedisService` returns 503 `IDEMPOTENCY_UNAVAILABLE` and writes nothing.
- Live reservation replay (catalog on `:4020`): same `reservationId` twice → 201 both times, stock 10 → 8, exactly one `sale` movement; release twice → stock 10, second call `items: []`; release after commit → 409 `RESERVATION_CLOSED`.
- No push, tag, release, or package publish was performed.
