# DESIGN DECISIONS (ADR log, append-only)

> Scope: locked decisions. Format: decision | date | choice | why | rules out.
> Status: Active | Date: 2026-09-30

| # | Decision | Date | Choice | Why | Rules out |
|---|---|---|---|---|---|
| 1 | Repo model | 2026-09-03 | Polyrepo, 12 repos | Independent pipelines, clear ownership, forces contract discipline (learning goal) | Monorepo workspaces |
| 2 | Frontend | 2026-09-03 | Next 16 + React 19 | SSR/ISR/SEO; Next 16 requires React 19 | Next 14 / plain Vite |
| 3 | Postgres access | 2026-09-30 | Raw SQL via `pg` (`Pool`), hand-written parameterized queries | Learn SQL properly, no ORM magic/binary, full index/join control for p99 | Prisma / TypeORM / query builders |
| 4 | Migrations | 2026-09-30 | None in v1 (schema applied manually/seed SQL) | Reduce moving parts while learning; revisit when schema churn demands it | Migration runners for now |
| 5 | Mongo | 2026-09-30 | Mongoose stays | Flexible CMS/analytics docs suit an ODM; only Postgres goes raw | Raw driver for Mongo |
| 6 | Events + tasks | 2026-10-01 | Self-hosted Kafka (all 10 domain events, every environment) + SQS (task queues: send-email, process-row, resize-image, reminders) | Ordered/replayable log where it matters ($0 extra), managed to-dos where it doesn't ($0–2/mo); MSK excluded (~$460+/mo); each workload on exactly one transport | Either/or dual transport; MSK; SQS-only |
| 7 | Contracts | 2026-09-03 | `@ecom/contracts` versioned npm, semver + CHANGELOG | Polyrepo needs a single truth with breaking-change windows | Cross-service imports |
| 8 | Scale | 2026-09-03 | Learning-based, NOT traffic-scale | Single EC2 + 1 broker + M0 intentionally; K8s/MSK later, same repo shape | Traffic-scale in v1 |
| 9 | Pagination | 2026-08-16 | Cursor (storefront) / offset (admin) | Stable inserts vs table UX | Offset everywhere |
| 10 | CMS publish | 2026-08-16 | save = publish v1 | Simplicity; drafts per-entity, not per-setting | Draft/live versioning in v1 |
| 11 | Dumb components | 2026-09-18 | Smart shell / dumb leaves; `??`/defaults only in resolvers | Readable, testable UI; see `skills/SKILL-DUMB.md` | Fetch/store in `ui/` |
| 12 | Edge transport boundary | 2026-10-14 | Browsers and serverless frontends reach backend only over HTTPS via the gateway (beacon/collect pattern); never direct Kafka or RDS connections | Serverless connection storms, public DB exposure | Direct broker/DB connections from edge |
