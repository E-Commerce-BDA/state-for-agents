# STATUS — Done / Now / Next

> Scope: human-readable mirror of `tasks.json`. Agents update both together.
> Status: Active | Date: 2026-10-27

## Done

- Documentation core `0–6`, `9–10`; component pioneers (Button/Icons/Tooltip + style contracts); `services/auth.md`; `pages/routing.md`; `pages/auth-design.md` (auth UI customization model, §6 demo implemented).
- `storefront-ui`: 14 `components/ui` primitives (Button→Tooltip + forms/feedback), `components/auth/*` composed blocks (AuthPage/Split/Panel/Form, PasswordMeter), `app/(auth)` routes (signin/signup/forgot + stateful islands, chromeless), `lib/auth/*` (settings vocabulary, resolver + sanitizer, cssVars, error map), `lib/cms/authSettings.ts` (cache-first fetcher), `AGENTS.md` constitution v1.0 (smart→pure→dumb, dumb-component guide, test trio, construct rules).
- Verification: `pnpm test` 111/111, `tsc` clean, `next build` green; commits C0–C9 pushed to `storefront-ui:main`.
- Skill system hardened: `LEARNING.md` root (teaching philosophy, step zero), router rewrite (dynamic default from `tasks.json`, task-protocol row, hooks row), skill contract enforced (SKILL-STOREFRONT paths fixed, SKILL-DUMB cites constitution, backend skills flagged structural-only), new `SKILL-HOOKS.md`, `archive/` retirement policy.
- Skills foldered smart-to-dumb (`explore/routes/hooks/lib/ui/services/project`, `hooks/` separate, `SKILL-` prefix kept, router-only index): EXPLORE split (SEARCHING + READING-DOCS), new `routes/SKILL-ROUTES.md`, all cross-links validated.
- Decisions locked: polyrepo, **raw SQL via `pg`, no migrations v1** (user ruling 2026-10-02 — overrides any Prisma text in older docs; see amendment task below), dual transport (Kafka local / SNS→SQS AWS), Next 16, ports-and-adapters hooks (sources injected, demo-first), learning mode always-on (`skip learning mode for this` to bypass).
- Auth service contract pinned 2026-10-23 (5 doc commits): liveness/readiness split with envelope + rate-limit exemptions (`4.API-Design.md §1.9`), `/api/v1` base path everywhere plus the no-trailing-slash forwarding rule, auth schema mechanics (app-generated UUID v7, `set_updated_at()` trigger, CASCADE, named constraints), password policy 8–128 with letter + digit, `services/auth.md` v1.1.
- Cart service contract pinned 2026-10-26 (15 doc commits): `services/cart.md` (identity, snapshots, CRUD, idempotency, registry-driven settings + audit, three merge policies, security, build/deploy, tests); schema §3.3 adds `cart.settings`/audit + guest-session uniqueness; API §3.3/§4.12 adds admin settings, required idempotency, `{item, cartTotals}`, 503; admin §3.21 + route; features A4.6 policy-driven; auth token/grace/merge aligned; testing §3.3; Nest 12/Node 24/Vitest docs.

## Now

- Shell slice (navbar system → `lib/shell/*` + `components/shell/*` + `app/hooks/*`, ports-first) per locked plan.
- File 0 done: `lib/shell/navSettings.ts` (agent-written on learner request 2026-10-02; learner resumes typing from File 1 `NavLinks.tsx`).
- `auth-svc` au-001: COMPLETE across all 10 slices (2026-10-25). `au-002` COMPLETE (2026-10-27): JWT issuer/audience. `au-003` COMPLETE (2026-10-27): shared error envelope. Final auth baseline: 29 unit + 37 e2e green, `oxlint` 0 errors/0 warnings, `nest build` clean.
- `cart-svc` COMPLETE across all 6 slices (`ca-001` through `ca-006`):
  - `ca-001` Phase 1 Base: PostgreSQL pool, `/health` and `/health/ready`, `001-cart-schema.sql`.
  - `ca-002` Settings Subsystem: `cart.settings`, `cart.settings_audit`, registry, versioned admin `GET/PATCH /api/v1/cart/settings`.
  - `ca-003` Cart CRUD: `CartIdentityGuard`, active-cart ensure, item mutations, catalog snapshots, Redis idempotency (`x-idempotency-key`), single post-commit `cart.updated`.
  - `ca-004` Guest Merge: `POST /cart/merge` for `merge`, `guest_wins`, `user_wins` with deterministic row locks.
  - `ca-005` Customer Wishlist: dual route `['wishlist', 'cart/wishlist']`, `@Roles('customer')`, lazy creation on `POST /wishlist/items`, duplicate idempotency, foreign delete 404, no cart events.
  - `ca-006` Hardening & Security: `GET /api/v1/cart/settings/audit` admin endpoint, `touchCart` enforcing `status = 'active'`, prototype pollution defenses, security e2e suite.
  - Final Verification: 13 unit test files (84/84 passed), 8 e2e test files (79/79 passed), 0 lint errors/warnings across 63 files, `nest build` clean exit 0.
- `catalog-svc` Phase 1 & 2 (`cat-001`) COMPLETE (2026-10-27):
  - Base foundation scaffolded per `SKILL-NEST-CLI.md` with bounded PostgreSQL pool (`src/db/pool.ts`).
  - Liveness (`/health`) and readiness (`/health/ready`) probes with DB liveness query and 503 on drop.
  - Complete `catalog` DDL schema in `001-catalog-schema.sql` (13 tables, GIN search vectors, navbar partial index, triggers).
  - Seed fixture catalog in `002-seed-catalog.sql` aligned with `cart-svc` fixtures.
  - Verification: 12 unit tests passed (3 test files), 16 e2e tests passed (2 test files), `oxlint` 0 warnings/0 errors on 29 files, `nest build` clean.
- `catalog-svc` Phase 3 (`cat-002`) COMPLETE (2026-10-27):
  - Categories subsystem: navbar query optimization (`idx_categories_navbar`), self-referencing tree builder, slug lookup, and admin CRUD with soft-deletes.
  - Brands subsystem: active index optimization (`idx_brands_active`), slug lookup, and admin CRUD with soft-deletes.
  - Shared auth: `JwtAuthGuard` + `RolesGuard` (`@Roles('admin')`) and standard `HttpExceptionFilter` error envelope.
  - Verification: 10 unit test files (50/50 passed), 4 e2e test files (38/38 passed), `oxlint` 0 warnings/0 errors across 55 files, `nest build` clean.
- `catalog-svc` Phase 4 (`cat-003`) COMPLETE (2026-10-27):
  - Products & PDP subsystem: single-join PDP query with PostgreSQL `json_agg` and `json_build_object` aggregating variants, gallery images, option definitions, and active discounts without N+1 round-trips.
  - Cursor pagination with multi-attribute filtering (category, brand, price range, status) and full-text search.
  - Admin CRUD endpoints for products, variants, option definitions, images, and scheduled discounts gated by `@Roles('admin')`.
  - Verification: 12 unit test files (61/61 passed), 5 e2e test files (55/55 passed), `oxlint` 0 warnings/0 errors across 72 files, `nest build` clean exit 0.
- `catalog-svc` Phase 5 (`cat-004`) COMPLETE (2026-10-27):
  - Stock ledger & movements: admin stock adjustments and history audit trail recording `qty_after` snapshots in `catalog.stock_movements`.
  - Atomic stock reservations: `POST /internal/stock/reserve` with row-level locks (`SELECT ... FOR UPDATE`), sorted deterministically to prevent deadlocks, with strict rollback on insufficient stock (`409 INSUFFICIENT_STOCK`).
  - Reservation compensation: `POST /internal/stock/release` to restore stock balance on order cancellation.
  - Verification: 16 unit test files (82/82 passed), 7 e2e test files (60/60 passed), `oxlint` 0 warnings/0 errors across 86 files, `nest build` clean exit 0.
- `catalog-svc` Phase 6 (`cat-005`) COMPLETE (2026-10-27):
  - Hardening & Security: Cache-Control policies configured across all endpoints (`public, max-age=60` on public catalog, `s-maxage=300, stale-while-revalidate=600` on navbar categories, `no-store` on internal/stock endpoints).
  - Prototype pollution & SQL injection defenses verified; standard error envelope and request ID correlation headers enforced.
  - Final Verification: 16 unit test files (82/82 passed), 8 e2e test files (67/67 passed), `oxlint` 0 warnings/0 errors across 87 files, `nest build` clean exit 0.
  - **`catalog-svc` IS NOW FULLY IMPLEMENTED AND VERIFIED.**
- `order-svc` Phase 1 (`ord-001`) COMPLETE (2026-10-27):
  - Base foundation scaffolded per `SKILL-NEST-CLI.md` with bounded PostgreSQL pool (`src/db/pool.ts`) and Redis client with `enableOfflineQueue: false` fail-closed policy (`src/redis/redis.service.ts`).
  - Liveness probe (`/health`) and readiness probe (`/health/ready`) verifying both PostgreSQL query (`SELECT 1`) and Redis ping (`PING`), with 503 response if either is down.
  - Nest CLI schematics generated for `health`, `db`, `redis`, `auth`, `discounts`, `checkout`, `orders`, `payments`, and `outbox`.
  - Global `ValidationPipe` and `/api/v1` prefix configured with health routes excluded.
  - Verification: 4 unit tests passed (1 file), 2 e2e tests passed (1 file), `oxlint` 0 warnings/0 errors on 25 files, `nest build` clean exit 0. 33 atomic commits recorded.
- `order-svc` Phase 2 (`ord-002`) COMPLETE (2026-10-27):
  - Full PostgreSQL DDL schema in `db/001-order-schema.sql` (7 tables: `orders`, `order_items`, `order_status_history`, `payments`, `outbox`, `discount_codes`, `shipments`).
  - Partial index `idx_outbox_pending` on `(status, created_at) WHERE status = 'pending'` for outbox relay poller.
  - Partial index `idx_discount_codes_valid` on `(is_active, ends_at) WHERE is_active` for fast coupon validation.
  - Test seed fixtures in `db/002-seed-orders.sql` with percent/fixed/expired/maxed coupons and sample order.
  - Strict TypeScript row types in `src/db/rows.ts` preserving decimal string representations.
  - Verification: 8/8 schema e2e tests passed (10/10 total e2e tests across 2 files), `oxlint` clean on 27 files, `nest build` clean exit 0. 4 atomic commits recorded.
- `order-svc` Phase 3 (`ord-003`) COMPLETE (2026-10-27):
  - Strict non-optional TypeScript DTOs for coupon validation, creation, update, and pagination (`ValidateDiscountCodeDto`, `CreateDiscountCodeDto`).
  - `DiscountsRepository` parameterized raw SQL queries with coupon normalization and atomic usage increments.
  - `DiscountsService` validation rules (active flag, start/end date windows, usage counts, minimum order thresholds) and percentage/fixed discount calculations clamped to cart totals.
  - `DiscountsController` exposing `POST /discount-codes/validate` (public/customer) and admin CRUD endpoints gated by `JwtAuthGuard` and `RolesGuard` with `@Roles('admin')`.
  - Verification: 17 unit tests passed (21 total unit tests), 14 e2e tests passed (24 total e2e tests across 3 files), `oxlint` 0 warnings/0 errors on 39 files, `nest build` clean exit 0. 16 atomic commits recorded.
- `order-svc` Phase 4 (`ord-004`) COMPLETE (2026-10-27):
  - Strict DTOs for checkout items, shipping and billing addresses, and payment provider request.
  - Cross-service client adapters: `CatalogClient` (`reserveStock`, `releaseStock`, `getProductSnapshots`) and `CartClient`.
  - `MockPaymentProvider` and `PaymentsService` for payment authorization and capture.
  - `CheckoutService` with Redis idempotency (`idem:{key}` 24h TTL, conflict detection, in-flight lock), saga-lite stock reservation compensation, and atomic single PostgreSQL transaction (`orders`, `order_items` snapshots, `order_status_history`, `payments`, `discount_codes` usage increment, and `outbox` row `order.created`).
  - Verification: 7 unit tests passed (28 total unit tests across 3 files), 6 e2e tests passed (30 total e2e tests across 4 files), `oxlint` clean on 49 files, `nest build` clean exit 0. 15 atomic commits recorded.
- `order-svc` Phase 5 (`ord-005`) COMPLETE (2026-10-27):
  - Strict DTOs for status updates, refunds, customer cursor pagination, and admin filtering.
  - Finite state machine (`order-state-machine.ts`) enforcing directional valid transitions (`pending` -> `confirmed` -> `processing` -> `shipped` -> `delivered` -> `refunded`).
  - `OrdersRepository` with customer cursor pagination, inline subquery relations, and atomic transactions.
  - `OrdersService` with RBAC ownership checks, state machine assertions, and refund limit validation.
  - `OutboxRepository` querying pending events with partial index `idx_outbox_pending` and `OutboxService` relay worker with polling, concurrency lock, and lifecycle hooks.
  - `CustomerOrdersController` and `OrdersController` mounting all customer and admin order endpoints.
- `order-svc` Phase 6 (`ord-006`) COMPLETE (2026-10-27):
  - Global `HttpExceptionFilter` with standard envelope `{ error: { code, message, details }, requestId, timestamp }` and `x-request-id` response header echoing.
  - `CacheControlInterceptor` enforcing `Cache-Control: no-store` on mutating HTTP methods.
  - `ServiceKeyGuard` enforcing `x-service-key` on `/internal/*` routes (`InternalController`).
  - Parameterized queries and UUID format validation preventing SQL injection and syntax errors.
  - Prototype pollution and forbidden parameter injection defenses via strict `ValidationPipe`.
  - Comprehensive service specification `Documentation/services/order.md` matching `auth.md` shape.
  - Verification: 45 unit tests passed across 5 test suites, 60 e2e tests passed across 6 test suites (105 total passing tests), `oxlint` clean on 65 files, `nest build` clean exit 0. 10 atomic commits recorded.
  - **`order-svc` is 100% COMPLETE across all 6 phases (`ord-001` through `ord-006`)**.

## Next (ordered)

1. Next service implementation (`cms-svc :4050` or `search-svc :4060`).
2. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) in storefront-ui.
3. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.

## Task tracking (57/57/0/1)

- `unpushed` array: every local commit not on `main` listed per repo
  until you push; cleared per-branch on push. Read push-state in `tasks.json`,
  never by asking. Latest: cart-svc 88 local commits (Phase 1 + schema 002 +
  ca-002/ca-003/ca-004 code/tests); Documentation 17 docs commits;
  state-for-agents 39 recorded tracker commits; auth-svc 14 hardening
  commits. The `tasks.json` carrier `15de2fa` and this STATUS commit join on
  the next update.

Per-task records live in `tasks.json` (`repos.*.tasks`) + `TASKS/` logs
(id == filename, status == folder). Auth: `au-001` done; `au-002` done; `au-003` done. Cart: `ca-001` done; `ca-002` done; `ca-003` done;
`ca-004` done; `ca-005`-`ca-006` todo. Backfill `sf-001`-`sf-010` done from session record; `sf-011` in
progress (learner-owned). `index.html` work is never logged (temporary
concept file).

## How to claim

Pick a `todo` in `tasks.json` (next todo `ca-005`) → set `claimedBy` + `in-progress` → load skills via `SKILL-ROUTER.md` → finish by flipping stage + updating here.
