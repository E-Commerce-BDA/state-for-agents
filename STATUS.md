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
- `cart-svc` ca-001: Phase 1 COMPLETE (2026-10-26). Foundation initialized, crash-proof connection pool to PostgreSQL `ecom-pg` (:5433), `/health` (liveness) & `/health/ready` (readiness) probes, `001-cart-schema.sql` applied (4 tables: `carts`, `cart_items`, `wishlists`, `wishlist_items`; 7 indexes including `one_active_cart_per_user` and `cart_items_cart_product_unique` with `NULLS NOT DISTINCT`; 2 triggers for `updated_at`). 12 unit tests + 12 e2e tests passing, `oxlint` 0 errors/0 warnings, `nest build` clean.
- Cart docs-first COMPLETE (2026-10-26): `services/cart.md` + schema/API/admin/features/auth/testing docs aligned; `ca-002` complete; `ca-003` complete; `ca-004` complete; `ca-005`-`ca-006` todo.
- `ca-002` COMPLETE (2026-10-27): settings registry + versioned admin GET/PATCH + append-only audit + JWT/`admin` guards + shared error envelope; `002-cart-settings.sql` applied to local `ecom-pg` with `cart.settings`, `cart.settings_audit`, audit indexes, `trg_cart_settings_updated_at`, `global` seed, and `one_active_cart_per_session`. Final cart baseline: 48 unit + 26 e2e green, `oxlint` 0 warnings, `tsc --noEmit`/`nest build` clean. Local DB restored to `global` / `{}` / version `0`; no test audit rows.
- `ca-003` COMPLETE (2026-10-27): active-cart ensure + item CRUD + snapshots/totals + Redis idempotency + one post-commit `cart.updated`. Identity resolves a verified JWT or the `x-session-id` cookie/header; malformed tokens never fall back to guest. `ecom-redis` is running on `:6379`; `ioredis` is committed. Final cart baseline: 74 unit + 46 e2e green, `oxlint` 0 warnings, `tsc --noEmit`/`nest build` clean. Local cleanup verified: 0 carts, 0 cart items, 0 `idem:*` Redis keys; settings still `global` / `{}` / version `0`.
- `ca-004` COMPLETE (2026-10-27): `POST /cart/merge` for `merge` (default), `guest_wins`, and `user_wins`, with deterministic row locks, never-lose-the-only-cart, guest `converted` history, idempotency, and one post-commit `cart.updated`. The identity guard carries `guestSessionId` alongside a verified user; merge reads `guestMergeStrategy` at request time and returns `{cart}` only. Final cart baseline: 79 unit + 58 e2e green (merge matrix 12), `oxlint` 0 warnings, `tsc --noEmit`/`nest build` clean. Local cleanup verified: 0 carts, 0 cart items, 0 audit rows; settings `global` / `{}` / version `0`; 0 `idem:*` Redis keys.
- `ca-005` docs COMPLETE (2026-10-27): global service-side role verification for role-sensitive routes; customer wishlist contract (verified JWT + `customer`, product-level, guest pending flow via `?next=`/short-lived cookie, no guest wishlist, no event/snapshot/idempotency, GET read-only). Code not started; `ca-005` remains todo.
- Known gap: `cart-svc/src/app.module.ts` remains uncommitted (existing `CartModule` import + `JWT_SECRET` validation); ca-003/ca-004 code is committed. The working tree is fully wired, but the cart-svc commit chain alone does not import `CartModule` until that file is committed. Concurrent item mutations still do not lock/verify the active cart status, so an add racing a merge can land in a converted cart; logged as a ca-004 follow-up.

## Next (ordered)

1. `ca-005` wishlist endpoints (code; `customer` role).
2. `ca-006` security/rate limits/audit read/observability hardening.
3. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) in storefront-ui.
4. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.
5. `ecom-contracts` v0.1, remaining 8 service specs (copy `services/auth.md` shape), missing component docs per `components/README.md`.

## Task tracking (55/52/1/3)

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
