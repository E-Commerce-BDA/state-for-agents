# SKILL ROUTER — when to use which skill

> Scope: task signal → skill chain. Load only what you need, in order.
> Status: Active | Date: 2026-09-30

| Task signal | Skills (in order) |
|---|---|
| Add/fix storefront section or card | SKILL-EXPLORE → SKILL-DUMB → SKILL-STOREFRONT → SKILL-CSS → SKILL-INTERFACES → SKILL-SEO |
| Add/fix admin screen | SKILL-EXPLORE → SKILL-DUMB → SKILL-ADMIN → SKILL-CSS → SKILL-INTERFACES |
| New/changed query or endpoint | SKILL-EXPLORE → SKILL-POSTGRES → SKILL-NESTJS → SKILL-INTERFACES → SKILL-FUNCTIONS |
| Cache/session/rate-limit bug | SKILL-REDIS → SKILL-NESTJS |
| CMS/blog content shape change | SKILL-MONGO → SKILL-NESTJS → SKILL-INTERFACES |
| New event or DTO change | SKILL-NESTJS → SKILL-INTERFACES → SKILL-FUNCTIONS (+ contracts semver note in DESIGN_DECISIONS #7) |
| Task backlog / email not sent / import stuck | SKILL-NESTJS (src/tasks/) → check task DLQ + job report → SKILL-REDIS only if idempotency-related |
| Styling/token bug | SKILL-CSS → SKILL-DUMB |
| New hook / hook behavior bug / service swap-in | SKILL-HOOKS → SKILL-INTERFACES → SKILL-DUMB |
| Deploy preview / env issue | SKILL-VERCEL |
| SEO/canonical/sitemap issue | SKILL-SEO → SKILL-FRONTEND |
| Don't know where to start | SKILL-EXPLORE → SKILL-FRONTEND or SKILL-NESTJS |

Each skill ends with "Use next:" links. Never invent paths — resolve via SKILL-EXPLORE.
