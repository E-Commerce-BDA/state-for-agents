# STATUS — Done / Now / Next

> Scope: human-readable mirror of `tasks.json`. Agents update both together.
> Status: Active | Date: 2026-10-23

## Done

- Documentation core `0–6`, `9–10`; component pioneers (Button/Icons/Tooltip + style contracts); `services/auth.md`; `pages/routing.md`; `pages/auth-design.md` (auth UI customization model, §6 demo implemented).
- `storefront-ui`: 14 `components/ui` primitives (Button→Tooltip + forms/feedback), `components/auth/*` composed blocks (AuthPage/Split/Panel/Form, PasswordMeter), `app/(auth)` routes (signin/signup/forgot + stateful islands, chromeless), `lib/auth/*` (settings vocabulary, resolver + sanitizer, cssVars, error map), `lib/cms/authSettings.ts` (cache-first fetcher), `AGENTS.md` constitution v1.0 (smart→pure→dumb, dumb-component guide, test trio, construct rules).
- Verification: `pnpm test` 111/111, `tsc` clean, `next build` green; commits C0–C9 pushed to `storefront-ui:main`.
- Skill system hardened: `LEARNING.md` root (teaching philosophy, step zero), router rewrite (dynamic default from `tasks.json`, task-protocol row, hooks row), skill contract enforced (SKILL-STOREFRONT paths fixed, SKILL-DUMB cites constitution, backend skills flagged structural-only), new `SKILL-HOOKS.md`, `archive/` retirement policy.
- Skills foldered smart-to-dumb (`explore/routes/hooks/lib/ui/services/project`, `hooks/` separate, `SKILL-` prefix kept, router-only index): EXPLORE split (SEARCHING + READING-DOCS), new `routes/SKILL-ROUTES.md`, all cross-links validated.
- Decisions locked: polyrepo, **raw SQL via `pg`, no migrations v1** (user ruling 2026-10-02 — overrides any Prisma text in older docs; see amendment task below), dual transport (Kafka local / SNS→SQS AWS), Next 16, ports-and-adapters hooks (sources injected, demo-first), learning mode always-on (`skip learning mode for this` to bypass).
- Auth service contract pinned 2026-10-23 (5 doc commits): liveness/readiness split with envelope + rate-limit exemptions (`4.API-Design.md §1.9`), `/api/v1` base path everywhere plus the no-trailing-slash forwarding rule, auth schema mechanics (app-generated UUID v7, `set_updated_at()` trigger, CASCADE, named constraints), password policy 8–128 with letter + digit, `services/auth.md` v1.1.

## Now

- Shell slice (navbar system → `lib/shell/*` + `components/shell/*` + `app/hooks/*`, ports-first) per locked plan.
- File 0 done: `lib/shell/navSettings.ts` (agent-written on learner request 2026-10-02; learner resumes typing from File 1 `NavLinks.tsx`).
- `auth-svc` au-001: COMPLETE across all 10 slices (2026-10-25). 17 unit tests + 36 e2e tests across 10 test suites green (`vitest`), `oxlint` 0 errors/0 warnings, `nest build` clean. Full implementation includes: Slice 1 health probes (`/health`, `/health/ready`); Slice 2 auth schema + seed (`001-auth-schema.sql`, `002-seed-roles.sql`); Slice 3 register (`POST /api/v1/auth/register`, Argon2id, 23505->409); Slice 4 login (`POST /api/v1/auth/login`, JWT HS256, SHA-256 refresh token hash); Slice 5 refresh rotation with 10s grace-period theft detection (`POST /api/v1/auth/refresh`); Slice 6 logout (`POST /api/v1/auth/logout`, 204 idempotent); Slice 7 `JwtAuthGuard` & profile (`GET /me`, `PATCH /me`); Slice 8 password change (`PATCH /me/password` with user-wide session revocation); Slice 9 address book CRUD (`/me/addresses` with single default constraint); Slice 10 admin RBAC & user management (`RolesGuard`, `@Roles('admin')`, `GET /users`, `PATCH /users/:id/status`, `GET/POST /roles`, `PATCH /users/:id/roles`). Next: Thin client in storefront-ui.

## Next (ordered)

1. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) replacing `TODO(auth-client)` stubs.
2. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.
3. `ecom-contracts` v0.1, remaining 8 service specs (copy `services/auth.md` shape), missing component docs per `components/README.md`.

## Task tracking (47/46/1/0)

- `unpushed` array (new): every local commit not on `main` listed per repo
  until you push; cleared per-branch on push. Read push-state in `tasks.json`,
  never by asking. Latest: auth-svc 45 local commits across all 10 slices
  (probes, schema, register, login, refresh, logout, profile, password, addresses, admin RBAC);
  Documentation 8 (2 earlier cart/envelope commits + 5 contract-slice commits + 1 family_id schema commit
  from 2026-10-23).

Per-task records live in `tasks.json` (`repos.*.tasks`) + `TASKS/` logs
(id == filename, status == folder). Backfill `sf-001`–`sf-010` done from
session record; `sf-011` in progress (learner-owned). `index.html` work is
never logged (temporary concept file).

## How to claim

Pick a `todo` in `tasks.json` → set `claimedBy` + `in-progress` → load skills via `SKILL-ROUTER.md` → finish by flipping stage + updating here.
