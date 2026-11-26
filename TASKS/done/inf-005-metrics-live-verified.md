# inf-005 — observability for lag, DLQ depth, outbox age and SQS age

- Repo: `ecom-infra`
- Phase: P5 · priority: P1 · kind: infra
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `9b09a72` (collector/config), `7451d54` (live collector fixes)
- Verified: **2026-11-26 against the live stack**

## What

`pnpm observe` exports Kafka lag, Kafka DLQ depth, per-producer outbox age,
SQS queue age and DLQ depth from the live stack into Prometheus text format.
Two collector bugs found only under live data were fixed in `7451d54`.

## Verification (live)

- `pnpm observe` emitted **57 valid Prometheus samples with zero `NaN`**.
- Concrete sample: `ecom_kafka_dlq_depth{topic="order.created.dlq"} 3674`,
  alongside per-store outbox age, SQS age/depth and consumer lag.
- Alarms/dashboards/runbook are checked by `pnpm check:observability`.
- Gates: `pnpm test:local` 53/53; all four `check:*` scripts green;
  `node --check` clean on every new/changed script.

## Caveat

A live alert firing was not exercised: no Prometheus/Alertmanager is deployed
here, so only the static rule check passed. That live alert path is covered by
`inf-009`, which was verified separately with a forced failed publish.

## Follow-ups

- None.
