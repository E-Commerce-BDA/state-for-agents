# PROJECT — E-Commerce Platform (agent intro)

> Scope: rough intro for agents joining this project. Docs are source of truth; this file points.
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/0.Project-Overview.md`

## What this is

Learning-focused, event-driven e-commerce platform. Polyrepo (13 repos, 1 deployable each):
`storefront-ui`, `admin-app`, `ecom-contracts` (`@ecom/contracts`), `ecom-messaging`
(`@ecom/messaging`: envelope + outbox store + relay + Kafka publisher), 9 NestJS services
(auth :4010, catalog :4020, cart :4030, order :4040, cms :4050, analytics :4060,
import :4070, notify :4080, search :4090), plus `ecom-infra` (compose/Nginx/VERSIONS.env).

Learning-based, NOT traffic-scale. Two transports, never both for one workload:
**Kafka carries domain events in every environment** (self-hosted KRaft, no env switch,
no SNS), and **SQS carries task jobs only**. Producers never publish from a handler:
all five of them (auth, cart, catalog, order, cms) write an outbox in the same
transaction as the domain change — `auth/cart/catalog/order.outbox` in Postgres,
`cms_outbox` in Mongo — and a `@ecom/messaging` 0.2.0 relay publishes it. There is no
second producer path left in any service.
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
