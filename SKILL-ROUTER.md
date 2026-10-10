# SKILL ROUTER — when to use which skill

> Scope: session bootstrap + task signal → skill chain. Load only what you
> need, in order. Default chain resolves from `tasks.json` `inProgress`
> (dynamic — today storefront-ui; follows whichever repo activates).
> Status: Active | Date: 2026-10-02

## Step zero (every session)

1. `LEARNING.md` — teaching philosophy, always active unless the bypass
   phrase was given.
2. This router — resolve the lane below, starting from the dynamic default.
3. Chained skills in order. Never invent paths — resolve via
   `explore/SKILL-SEARCHING.md`.

| Task signal | Skills (in order) |
|---|---|
| Storefront section/card/auth (dynamic default while `storefront-ui` is in-progress) | `explore/SKILL-EXPLORE.md` → `explore/SKILL-SEARCHING.md` → `ui/SKILL-DUMB.md` → `hooks/SKILL-HOOKS.md` (if stateful) → `routes/SKILL-ROUTES.md` → `routes/SKILL-STOREFRONT.md` → `ui/SKILL-CSS.md` → `lib/SKILL-INTERFACES.md` → `project/SKILL-SEO.md` |
| Add/fix admin screen | `explore/SKILL-EXPLORE.md` → `ui/SKILL-DUMB.md` → `routes/SKILL-ADMIN.md` → `ui/SKILL-CSS.md` → `lib/SKILL-INTERFACES.md` |
| New/changed query or endpoint | `explore/SKILL-EXPLORE.md` → `services/SKILL-POSTGRES.md` → `services/SKILL-NESTJS.md` → `lib/SKILL-INTERFACES.md` → `lib/SKILL-FUNCTIONS.md` |
| Cache/session/rate-limit bug | `services/SKILL-REDIS.md` → `services/SKILL-NESTJS.md` |
| CMS/blog content shape change | `services/SKILL-MONGO.md` → `services/SKILL-NESTJS.md` → `lib/SKILL-INTERFACES.md` |
| New event or DTO change | `services/SKILL-NESTJS.md` → `lib/SKILL-INTERFACES.md` → `lib/SKILL-FUNCTIONS.md` (+ contracts semver note in DESIGN_DECISIONS #7) |
| Task backlog / email not sent / import stuck | `services/SKILL-NESTJS.md` (src/tasks/) → check task DLQ + job report → `services/SKILL-REDIS.md` only if idempotency-related |
| New hook / hook behavior bug / service swap-in | `hooks/SKILL-HOOKS.md` → `lib/SKILL-INTERFACES.md` → `ui/SKILL-DUMB.md` |
| Claim/close/status task protocol | `tasks.json` workflow block (no skill file — protocol stays there until it outgrows ~10 lines) |
| Styling/token bug | `ui/SKILL-CSS.md` → `ui/SKILL-DUMB.md` |
| Animation/motion bug or new animated surface | `ui/SKILL-MOTION.md` → `ui/SKILL-CSS.md` → `ui/SKILL-DUMB.md` |
| Deploy preview / env issue | `project/SKILL-VERCEL.md` |
| SEO/canonical/sitemap issue | `project/SKILL-SEO.md` → `routes/SKILL-ROUTES.md` |
| Don't know where to start | `explore/SKILL-EXPLORE.md` → `explore/SKILL-SEARCHING.md` |

Repo constitutions (e.g. storefront `AGENTS.md`) win local conflicts; the
discovering agent files the skill amendment as a task the same turn.
Retired skills move to `archive/` (links removed, history preserved).
