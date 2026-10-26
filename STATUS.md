# STATUS — Done / Now / Next

> Scope: human-readable mirror of `tasks.json`. Agents update both together.
> Status: Active | Date: 2026-10-26

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
- `auth-svc` au-001: COMPLETE across all 10 slices (2026-10-25). 17 unit tests + 36 e2e tests across 10 test suites green (`vitest`), `oxlint` 0 errors/0 warnings, `nest build` clean. `au-002` COMPLETE (2026-10-27): JWT issuer/audience, 24 unit + 37 e2e green. `au-003` shared error envelope queued.
- `cart-svc` ca-001: Phase 1 COMPLETE (2026-10-26). Foundation initialized, crash-proof connection pool to PostgreSQL `ecom-pg` (:5433), `/health` (liveness) & `/health/ready` (readiness) probes, `001-cart-schema.sql` applied (4 tables: `carts`, `cart_items`, `wishlists`, `wishlist_items`; 7 indexes including `one_active_cart_per_user` and `cart_items_cart_product_unique` with `NULLS NOT DISTINCT`; 2 triggers for `updated_at`). 12 unit tests + 12 e2e tests passing, `oxlint` 0 errors/0 warnings, `nest build` clean.
- Cart docs-first COMPLETE (2026-10-26): `services/cart.md` + schema/API/admin/features/auth/testing docs aligned; `ca-002`–`ca-006` are todo. Next implementation slice: `ca-002` settings subsystem (schema 002, registry, admin API, audit, JWT + `admin` guard).
- Known gaps: `auth-svc` `au-003` shared error envelope queued; `services/auth.md` documents the shared envelope as the target. `cart-svc` has uncommitted `src/app.module.ts` and untracked `src/cart/` stubs - left untouched.

## Next (ordered)

1. `au-003` auth shared error envelope: global filter, `APP_FILTER`, tests.
2. `ca-002` settings subsystem: `002-cart-settings.sql`, registry, versioned admin API, audit, JWT + `admin` guard.
3. `ca-003` active-cart ensure + item CRUD + totals + idempotency + `cart.updated`.
4. `ca-004` guest merge policies (`merge`, `guest_wins`, `user_wins`).
5. `ca-005` wishlist endpoints.
6. `ca-006` security/rate limits/audit read/observability hardening.
7. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) in storefront-ui.
8. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.
9. `ecom-contracts` v0.1, remaining 8 service specs (copy `services/auth.md` shape), missing component docs per `components/README.md`.

## Task tracking (55/48/1/6)

- `unpushed` array: every local commit not on `main` listed per repo
  until you push; cleared per-branch on push. Read push-state in `tasks.json`,
  never by asking. Latest: cart-svc 23 local commits (Phase 1); Documentation
  15 docs commits; state-for-agents tracker commits; auth-svc 0 (synced).
  The `tasks.json` carrier that records this list joins on the next update.

Per-task records live in `tasks.json` (`repos.*.tasks`) + `TASKS/` logs
(id == filename, status == folder). Auth: `au-001` done; `au-002` done; `au-003` todo. Cart: `ca-001` done; `ca-002`-`ca-006`
todo. Backfill `sf-001`-`sf-010` done from session record; `sf-011` in
progress (learner-owned). `index.html` work is never logged (temporary
concept file).

## How to claim

Pick a `todo` in `tasks.json` (start with `au-003`) → set `claimedBy` + `in-progress` → load skills via `SKILL-ROUTER.md` → finish by flipping stage + updating here.
