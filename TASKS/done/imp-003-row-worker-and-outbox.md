# imp-003 — row worker and product.imported outbox (done, 2026-11-25)

- Repos: `import-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: sqs-consumer
- Started: 2026-11-25 | Finished: 2026-11-25

## What

The worker long-polls `import-process-row` in batches of 10. It maps each row
into `productImportedPayloadSchema`, writes the event into `import.outbox`, and
marks `import_rows` processed in one Postgres transaction. The relay publishes
the stored envelope; import-svc has no Kafka consumer.

A row without a valid `id` gets a minted UUID stored in `import_rows.product_id`
and used as the Kafka key. The slug comes from `row.slug` or the name; status
defaults to `active`; `updatedAt` is server time. A row that cannot satisfy the
contract is marked failed and acknowledged. A transient database error is
thrown so SQS redrives into `import-process-row-dlq`. A redelivery of a
processed row takes a row lock, sees `processed`, and writes nothing.

## Why

The row status and the event must not diverge, so the outbox write and the row
update share a transaction. Retry cannot fix a bad payload, so validation
failures are terminal; a database blip can be retried, so that error propagates.
A minted id keeps the existing upload validation (sku/name/price only) while
still giving the event a stable key.

## How

- `db/002-import-outbox.sql` — outbox with catalog's envelope and aggregate
  invariants, constrained to `product.imported`.
- `src/outbox/` — `createOutboxModule` for the `import` schema and the record
  method.
- `src/worker/` — pure row mapper, handler with row lock, handler token module.
- `import.module.ts` now supplies the worker token and enables the poller with
  `SQS_TASKS_ENABLED=true`.
- Commits: `1a1fdb3` (service), `3ff73cb` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 31 tests / 8 files |
| `pnpm test:e2e` | 2 tests / 1 file |
| `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply both migrations when Postgres is available.
- Live LocalStack/Kafka verification remains outstanding.
