# ARCHITECTURE (condensed, 1 page)

> Scope: 1-page arch summary for agents. Full spec: `Documentation/1.Architecture.md`.
> Status: Active | Date: 2026-09-30

- **Request path:** Browser → Nginx (`storefront./admin./api.` domains) → Next.js apps (:3000/:3001) or NestJS service by `/api/<route>` prefix → Postgres/Mongo/Redis.
- **Event path:** services inject `IEventBus.publish/subscribe` only. `KafkaBus` when `TRANSPORT=kafka` (local, topics + DLQ topics + replay), `SnsSqsBus` when `TRANSPORT=sqs` (AWS, SNS→per-consumer SQS, FIFO where ordered, redrive DLQ, no replay). Envelope identical (`@ecom/contracts`).
- **Data:** DB-per-service, FKs only inside own schema; cross-service refs = logical UUID. `order-svc` outbox (order + outbox in one TX) + idempotency keys everywhere; saga-lite compensation on stock fail.
- **Frontend:** Server Components fetch + `lib/cms/resolve.ts` (P>S>G) → dumb props; smart state only in route islands + `store/`.
- **Deploy:** per-repo image → GHCR, `ecom-infra/VERSIONS.env` pins tags; one service at a time; rollback = revert one line. Health `/health` + `/health/ready`, `x-request-id` tracing, CloudWatch alarms.
