# ARCHITECTURE (condensed, 1 page)

> Scope: 1-page arch summary for agents. Full spec: `Documentation/1.Architecture.md`.
> Status: Active | Date: 2026-10-30

- **Request path:** Browser → Nginx (`storefront./admin./api.` domains) → Next.js apps (:3000/:3001) or NestJS service by `/api/<route>` prefix → Postgres/Mongo/Redis.
- **Event path:** services inject `IEventBus.publish/subscribe` only, and the impl is `KafkaBus` in **every** environment (self-hosted KRaft; no env switch and no SNS adapter): topics + `.dlq` twins + replay, one consumer group per service (`postfixId` empty), `processed_events` dedupe. `ITaskQueue` (`SqsTaskQueue`) carries jobs only — `notify.send-email`, `import.process-row`, `media.resize-image`. `cms.updated` has **no** Kafka consumer (storefront invalidation is the cms-svc `/api/revalidate` webhook), and storefront/admin hold no broker credentials: page views go `Next /api/track` → `analytics-svc` → Kafka. Envelope identical (`@ecom/contracts`).
- **Data:** DB-per-service, FKs only inside own schema; cross-service refs = logical UUID. `order-svc` outbox (order + outbox in one TX) + idempotency keys everywhere; saga-lite compensation on stock fail.
- **Frontend:** Server Components fetch + `lib/cms/resolve.ts` (P>S>G) → dumb props; smart state only in route islands + `store/`.
- **Deploy:** per-repo image → GHCR, `ecom-infra/VERSIONS.env` pins tags; one service at a time; rollback = revert one line. Health `/health` + `/health/ready`, `x-request-id` tracing, CloudWatch alarms.
