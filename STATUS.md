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

## Next (ordered)

1. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) in storefront-ui.
2. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.
3. `ecom-contracts` v0.1, remaining 8 service specs (copy `services/auth.md` shape), missing component docs per `components/README.md`.

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
