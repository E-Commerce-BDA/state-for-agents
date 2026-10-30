# doc-001 — correct the event transport claims

- Repo: `Documentation` + `state-for-agents` (condensed page only)
- Phase: P0 · kind: docs · transport: docs
- Started: 2026-10-30 · Finished: 2026-10-30

## What the defect was

Three documents described a transport that does not exist, and each wrong claim
produces a wrong implementation:

1. `1.Architecture.md` drew `storefront`/`admin` publishing into Kafka, listed a
   `cms-svc` consumer for `product.imported` and `cms.updated`, described
   consumer groups per (service, topic), carried 10 topics instead of 11, kept a
   `reminder.dispatch` queue, and put an email address in the
   `user.registered` payload.
2. `2.Tech-Stack.md` labelled the broker `Kafka local: KRaft / AWS: SNS→SQS`,
   drew `SF --> K` and `AD --> K`, gave the frontend a KafkaJS row, described
   `@nestjs/microservices` as request-reply, and listed a `src/events/` +
   `src/jobs/` + `dtos/` + `openapi/` contracts layout that the package does not
   have.
3. `state-for-agents/ARCHITECTURE.md` told agents to expect an `IEventBus`
   implementation switch (`TRANSPORT=kafka` → `KafkaBus`, `TRANSPORT=sqs` →
   `SnsSqsBus`) that was removed.

Scope stayed exactly the three files the user chose; every other doc that is
still stale is recorded as a follow-up instead of being silently edited.

## How it was fixed

### `1.Architecture.md`

- §3 diagram: browser→broker edges deleted; each service now shows
  `publish events → KAFKA` and/or `publish tasks → TASKS` as separate edges;
  `analytics-svc` is the `page.viewed` producer; `search-svc` consumes events;
  Kafka label "10 domain events" → "11 topics".
- §4 table: `catalog-svc` produces `product.updated`/`category.updated` and
  consumes `order.status.updated`; `cart-svc` consumes `—` with the `ca-009`
  conversion consumer named as future work and `ca-007` as the Phase-0 bridge;
  `cms-svc` consumes `—`; `analytics-svc` no longer consumes `page.viewed`.
- §6.3: canonical-source blockquote (`tasks.json#messaging.topics` ← mirrored by
  `EVENT_TOPICS`) and the full 11-row table with a producer → consumers column;
  `cart.updated` is keyed by `cartId`.
- §6.4: mermaid gains the `analytics-svc` producer, `cms.updated` (T10),
  `order.status.updated` (T11) and all 11 `.dlq` twins; "one consumer group per
  service (`postfixId` empty)" replaces the per-(service, topic) wording;
  `T2 --> cart-svc` is deliberately absent with the reason written next to it.
- §6.5/§6.6: "No fan-out service in v1 — one queue per job type, so nothing
  publishes through SNS"; three task queues; schema path
  `src/schemas/jobs.ts`.
- §7.6 producer `storefront` → `analytics-svc`; §7.7 drops `email` and gains the
  PII-minimization note (`GET /internal/users/:id/email`, au-005); §11
  invalidation split into Kafka consumers (`product.imported`) and the CMS HTTP
  webhook; §12 SQS row loses `reminder.dispatch`; §15.2/§15.4 sequences route
  beacons through `Next /api/track`; §15.3 loses the imaginary CMS consumer.

### `2.Tech-Stack.md`

- §1: `K[(Kafka: self-hosted KRaft, every env)]` + an SQS node in the bus
  subgraph; `SF --> K` and `AD --> K` deleted with a comment explaining why.
- §2 principle 6, §3 `tasks/` + `aws/sqs.tf`, §4 SQS row and §7 infra row: three
  queues, no `reminders`.
- §3 contracts layout replaced with the shipped tree (`src/index.ts`,
  `src/schemas/{events,topics,jobs,media}.ts`, `test/`); no `dtos/`, no
  `openapi/`.
- §4 KafkaJS row → "not used in the frontend"; §5 `@nestjs/microservices` →
  consumers only, manual commit, DLQ, producers via outbox + kafkajs; §6
  "Any NestJS service".
- `Last Updated: 2026-09-03` → `2026-10-30`.

### `state-for-agents/ARCHITECTURE.md`

- Event-path bullet rewritten: `KafkaBus` in **every** environment, no transport
  switch and no SNS adapter, `.dlq` twin per topic, one consumer group per
  service, `processed_events` dedupe, SQS for the three jobs, `cms.updated` has
  no Kafka consumer, browsers hold no credentials. `Date:` refreshed.

## Decisions and rejected alternatives

| Decision | Why | Rejected alternative |
|---|---|---|
| Grep for real claims, allow negations | The verification regex flags the very sentences that remove the wrong claim ("not one group per topic", "no env switch"). Rephrasing them to zero hits keeps the gate literal and the sentence truthful. | Keep `SnsSqsBus`/`(service, topic)` inside negations and argue the two hits are fine — an agent grepping the doc later would still land on the removed names. |
| Write the **real** contracts tree, not `src/events/` + `src/jobs/` | The plan's `src/events/`/`src/jobs/` wording was itself stale; `pnpm ls @ecom/contracts` shows `src/schemas/*`. Documenting a layout that does not exist recreates the defect being fixed. | Copy the plan literally (`src/events/` = "envelope, topic registry, 11 payload types"). |
| Keep §7.2's `email` field, fix only §7.7 | doc-001's acceptance names §7.7; `cart.abandoned` is a target contract under anl-002 and its payload is being redesigned there. | Sweep every `email` in the doc — scope creep into a self-consumed analytics payload. |
| Leave §7.1–7.5 payload drift alone | Out of transport scope; the drift is recorded as a follow-up so the next contracts task fixes examples and schemas together. | Rewrite all nine examples now, in a plan that never reviewed them. |
| Edit `state-for-agents/ARCHITECTURE.md` in its own commit | Different repo (polyrepo rule), different audience (agents, not humans). | Fold it into the Documentation commit. |

## Verification

- Plan regex over the three files: `SNS\s*(→|->)\s*SQS|SnsSqsBus|SNS fan-out|TRANSPORT=|reminder\.dispatch|per \(service, topic\)|storefront.{0,40}Kafka` → **0 hits**.
- §6.3 has **11** topic rows; `cms.updated` present; `page.viewed` producer is
  `analytics-svc`; §7.7 has no `"email"` (the single remaining `"email"` in the
  file is §7.2 `cart.abandoned`, intentionally untouched).
- `git log` shows one commit per file and no stray files (`git status` clean in
  both repos).

Commits:

- `Documentation` `d02aa48` — `docs(architecture): correct the event transport claims`
- `Documentation` `10e38de` — `docs(tech-stack): remove the SNS to SQS and storefront Kafka claims`
- `state-for-agents` `159e8eb` — `docs(agents): rewrite the condensed event path`

## Open

- Payload examples §7.1–§7.5 predate contracts 1.4.0 (`cart.updated` items,
  `order.created` totals, `order.status.updated`, `product.imported`); they need
  a doc pass that reads `src/schemas/events.ts`.
- `0.Project-Overview.md`, `4.API-Design.md` §1.8/§6.6, `5.Features.md` header,
  `6.Admin-Panel.md` ~L351, `9.Testing.md` fan-out row, `PROJECT.md`, and
  `DESIGN_DECISIONS.md` row 6 still carry the old claims.
- `2.Tech-Stack.md` still pins `ioredis 5.x` (shipped 6.x) and keeps a KafkaJS
  row in the frontend table as an explicit non-use.
