# PROJECT — E-Commerce Platform (agent intro)

> Scope: rough intro for agents joining this project. Docs are source of truth; this file points.
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/0.Project-Overview.md`

## What this is

Learning-focused, event-driven e-commerce platform. Polyrepo (12 repos, 1 deployable each):
`storefront-ui`, `admin-app`, `ecom-contracts` (`@ecom/contracts`), 9 NestJS services
(auth :4010, catalog :4020, cart :4030, order :4040, cms :4050, analytics :4060,
import :4070, notify :4080, search :4090), plus `ecom-infra` (compose/Nginx/VERSIONS.env).

Learning-based, NOT traffic-scale. Dual transport via `IEventBus`:
`TRANSPORT=kafka` locally (self-hosted KRaft) / `TRANSPORT=sqs` on AWS (SNS→SQS).
Postgres via **raw SQL + `pg`** (no ORM, no migrations in v1); Mongoose stays for Mongo.

## How to work

1. Read `state-for-agents/STATUS.md` + `SERVICES.md` (or `tasks.json`) — pick a `todo` task.
2. Claim it: set `claimedBy` + `in-progress` in `tasks.json` (and mirror in `STATUS.md`).
3. Follow `SKILL-ROUTER.md` to load only the skills you need.
4. Specs live in `Documentation/` — never duplicate them here; link to owner doc.
5. Finish: flip stage to `done` in `tasks.json` + `STATUS.md` in the same commit.

## Reading order

`PROJECT.md` → `SERVICES.md`/`STATUS.md` → owner doc in that row → skills via router.
Key docs: `0.Project-Overview.md` (vision), `1.Architecture.md` (dual transport),
`2.Tech-Stack.md` (polyrepo), `9.Testing.md` (SLOs), `10.Observability.md` (alarms).
