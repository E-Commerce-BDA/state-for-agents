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
- ORM check closed 2026-10-02: full Documentation grep found zero Prisma/ORM/migration references (docs already raw-SQL) — no amendment needed, nothing committed.
- `auth-svc` au-001: health split done 2026-10-23 — `/health` is dependency-free liveness (`{"status":"ok"}`), `/health/ready` probes Postgres and returns the exact `503 {"status":"not_ready","checks":{"db":"down"}}`. Trip-the-guard live: 200/200 → DB stop → **200/503** → DB start → 200/200 with no process restart. Slice 2 auth schema + role seeds done 2026-10-23: `001-auth-schema.sql` (7 tables, 8 explicit indexes, 4 updated_at triggers, CASCADE delete), `002-seed-roles.sql` (`admin`, `customer`), `db/README.md`, `test/schema.e2e-spec.ts` (11/11 tests green). Slice 3 register slice done: `RegisterDTO` (8-128 chars, lowercase email, validation pipe), `AuthService` with Argon2id, raw SQL transaction (`BEGIN`/`COMMIT`/`ROLLBACK`), `23505` duplicate email mapped to 409 Conflict, `assignUserRole` default 'customer', `POST /api/v1/auth/register` in `AuthController`, and `test/register.e2e-spec.ts` (4 e2e tests covering 201, 409, and 400 cases); 17 unit + 19 e2e green. Next: Slice 4 login slice.

## Next (ordered)

1. Thin client (`lib/auth/client.ts` + per-action handlers + `proxy.ts`) replacing `TODO(auth-client)` stubs.
2. CMS source wiring replacing `TODO(cms-svc)` null-sources; `7.Deployment.md` + `8.Versioning.md` stubs.
3. `ecom-contracts` v0.1, remaining 8 service specs (copy `services/auth.md` shape), missing component docs per `components/README.md`.
4. auth-svc au-001 remainder: register slice (DTO/APP_PIPE, argon2id, 23505→409, UUID v7) → login/refresh/logout.

## Task tracking (47/46/1/0)

- `unpushed` array (new): every local commit not on `main` listed per repo
  until you push; cleared per-branch on push. Read push-state in `tasks.json`,
  never by asking. Latest: auth-svc 11 local commits (pool crash fix, health
  tests, prettier, :4010 port, 3 health-split commits + 4 schema commits: 001
  DDL, 002 seed, db README, schema e2e); Documentation 8 (2 earlier
  cart/envelope commits + 5 contract-slice commits + 1 family_id schema commit
  from 2026-10-23).

Per-task records live in `tasks.json` (`repos.*.tasks`) + `TASKS/` logs
(id == filename, status == folder). Backfill `sf-001`–`sf-010` done from
session record; `sf-011` in progress (learner-owned). `index.html` work is
never logged (temporary concept file).

## How to claim

Pick a `todo` in `tasks.json` → set `claimedBy` + `in-progress` → load skills via `SKILL-ROUTER.md` → finish by flipping stage + updating here.
