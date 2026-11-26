# inf-009 — relay, lag and queue metrics with alerts

- Repo: `ecom-infra`
- Phase: P5 · priority: P1 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `4686dca` (relay/alert config), `7451d54` (collector fixes)
- Verified: **2026-11-26 against the live stack**

## What

The relay collector exports failed-row count, oldest pending age and relay lock
age per producer; lag and queue age share the same dashboard. Alerts are
defined in `observability/relay-alerts.json`.

## Verification (live)

- A forced auth outbox row reached `failed/5` during a Kafka outage.
- `ecom_outbox_failed_rows{store="auth"} 1` was exported and the
  `outbox-failed-rows` alert evaluated **active** for auth and order.
- Relay lease observation during retry backoff: `28.29s` remaining and
  `relay_lock_held{store="auth"} 1`.
- Gates: `pnpm test:local` 53/53; `check:observability` and the other static
  checks green.

## Follow-ups

- None.
