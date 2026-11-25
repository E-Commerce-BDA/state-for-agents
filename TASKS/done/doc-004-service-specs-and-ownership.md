# doc-004 — service specs and event ownership (done, 2026-11-25)

- Repos: `Documentation`
- Phase: P4 | priority: P1 | kind: docs | transport: docs
- Started: 2026-11-25 | Finished: 2026-11-25

## What

Added a transport-ownership table to all nine service specs, derived from
`STATUS.md` section 5: Kafka publishes with keys, Kafka consumes, SQS task
queues and an explicit "must not" boundary. Fixed the two stale rows in
`1.Architecture.md` section 5 — analytics consumes `page.viewed` too, and
import-svc owns a Postgres schema with an outbox rather than being stateless.
Updated the notify and import appendices to name their real directories and
removed scaffold-only wording.

The event ownership matrix in section 6.3 already matched the live code, so it
was left alone.

## Why

Ownership stated only in prose drifts from the code. One canonical table,
referenced by each spec, makes a false claim visible in review. The "must not"
row matters more than the positive rows: the common documentation error is
claiming a consumer or producer that does not exist.

## How

- Script appended a standard table to `auth/cart/catalog/order/cms/search/notify/analytics/import.md`.
- Two architecture rows and two spec appendices corrected.
- Commit: `be52490` in `Documentation`.

## Verification

No code changed; gates are the existing repo gates. A grep of the nine specs
shows one transport-ownership table each, and no spec claims an unowned
producer or consumer.

## Follow-ups

Historical task IDs remain in some specs; they are records, not current-state
claims.
