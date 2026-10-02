# SKILL ROUTER — when to use which skill

> Scope: session bootstrap + task signal → skill chain. Load only what you
> need, in order. Default chain resolves from `tasks.json` `inProgress`
> (dynamic — today storefront-ui; follows whichever repo activates).
> Status: Active | Date: 2026-10-02

## Step zero (every session)

1. `LEARNING.md` — teaching philosophy, always active unless the bypass
   phrase was given.
2. This router — resolve the lane below, starting from the dynamic default.
3. Chained skills in order. Never invent paths — resolve via SKILL-EXPLORE.

| Task signal | Skills (in order) |
|---|---|
| Storefront section/card/auth (dynamic default while `storefront-ui` is in-progress) | SKILL-EXPLORE → SKILL-DUMB → SKILL-HOOKS (if stateful) → SKILL-STOREFRONT → SKILL-CSS → SKILL-INTERFACES → SKILL-SEO |
| Add/fix admin screen | SKILL-EXPLORE → SKILL-DUMB → SKILL-ADMIN → SKILL-CSS → SKILL-INTERFACES |
| New/changed query or endpoint | SKILL-EXPLORE → SKILL-POSTGRES → SKILL-NESTJS → SKILL-INTERFACES → SKILL-FUNCTIONS |
| Cache/session/rate-limit bug | SKILL-REDIS → SKILL-NESTJS |
| CMS/blog content shape change | SKILL-MONGO → SKILL-NESTJS → SKILL-INTERFACES |
| New event or DTO change | SKILL-NESTJS → SKILL-INTERFACES → SKILL-FUNCTIONS (+ contracts semver note in DESIGN_DECISIONS #7) |
| Task backlog / email not sent / import stuck | SKILL-NESTJS (src/tasks/) → check task DLQ + job report → SKILL-REDIS only if idempotency-related |
| New hook / hook behavior bug / service swap-in | SKILL-HOOKS → SKILL-INTERFACES → SKILL-DUMB |
| Claim/close/status task protocol | `tasks.json` workflow block (no skill file — protocol stays there until it outgrows ~10 lines) |
| Styling/token bug | SKILL-CSS → SKILL-DUMB |
| Deploy preview / env issue | SKILL-VERCEL |
| SEO/canonical/sitemap issue | SKILL-SEO → SKILL-FRONTEND |
| Don't know where to start | SKILL-EXPLORE → SKILL-FRONTEND or SKILL-NESTJS |

Each skill ends with "Use next:" links. Repo constitutions (e.g. storefront
`AGENTS.md`) win local conflicts; the discovering agent files the skill
amendment as a task the same turn. Retired skills move to `archive/` (links
removed, history preserved).
