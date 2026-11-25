# imp-002 — upload API and SQS row producer (done, 2026-11-25)

- Repos: `import-svc` (+ `Documentation`)
- Phase: P4 | priority: P0 | kind: feature | transport: sqs-producer
- Started: 2026-11-25 | Finished: 2026-11-25

## What

`POST /api/v1/import` accepts a multipart CSV or JSON file behind a JWT admin
guard. The request parses the file with csv-parse, writes `import_jobs` and one
`import_rows` row per source row in one Postgres transaction, and returns
`202 {jobId}`. It then enqueues one `import-process-row` task per valid row with
idempotency key `import-row:<jobId>:<rowNumber>`. `GET /jobs` and `/jobs/:id`
expose the batch report. No Kafka code is involved.

A row missing `sku`, `name` or `price` is stored failed with an error and not
enqueued. A SKU seen earlier in the same file is failed with `duplicate-sku`.
Neither rejects the file. A queue refusal marks only that row failed.

## Why

One task per row isolates bad rows and lets a redelivery update the same
`import_rows` row instead of appending another. Processing rows inline would
block the request on a large file. All-or-nothing validation would lose the
good rows because of one bad one.

The admin routes reuse auth-svc's issuer, audience, algorithm and clock
tolerance so they cannot drift from the other services' guards.

## How

- `src/import/parse-upload.ts` — pure CSV/JSON parse and per-row validation.
- `src/import/import.service.ts` — transactional job/row write, enqueue, report.
- `src/import/import.controller.ts` — guarded upload and job reads.
- `src/import/import-task-publisher.ts` and `import.module.ts` — producer-only
  SQS module; poller opt-in, worker arrives in imp-003.
- Commits: `1e533e4` (service), `3be3da9` (Documentation).

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 21 tests / 5 files |
| `pnpm test:e2e` | 2 tests / 1 file |
| `pnpm lint` / `pnpm build` | green |

## Follow-ups

- Apply the migration before running the upload path against real Postgres.
- imp-003 adds the worker and the `product.imported` publisher.
- Live LocalStack verification of the producer remains outstanding.
