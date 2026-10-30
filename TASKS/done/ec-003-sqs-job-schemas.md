# ec-003 — contracts 1.8.0: SQS job schemas and the queue registry

- Repo: `ecom-contracts` (+ `ecom-infra` repin)
- Phase: P1 · priority: P0 · kind: feature · transport: contracts
- Started: 2026-10-30 · Finished: 2026-10-30
- Commits: `1d92d1c` (schemas, tests, changelog, tarball), `fcc8658` (VERSIONING rule + tarball refresh)

## What

`@ecom/contracts@1.8.0` adds the SQS half of the messaging surface. Until now
`jobs.ts` held one schema (`resizeImageJobSchema`) and the queue names existed
only in prose.

`src/schemas/jobs.ts`:

| Schema | Shape |
|---|---|
| `sendEmailJobSchema` | `template` (`order-confirmation` \| `cart-abandoned` \| `welcome`), optional `userId`/`orderId`/`cartId`, optional `locale`, required `idempotencyKey` (1–128); `.strict()` + refine requiring at least one aggregate |
| `processImportRowJobSchema` | `jobId` (≤64), `rowNumber` (positive int), `source` (`csv` \| `json`), `stockMode` (`replace` \| `add`), `row` as `record<string, string\|number\|boolean\|null>` |
| `resizeImageJobSchema` | unchanged |

Plus `emailTemplateSchema`, `importSourceSchema`, `importStockModeSchema`,
`importRowValueSchema` and their inferred types.

`src/schemas/queues.ts` is new: `TASK_QUEUES` (three entries with `queue`, `dlq`,
`producer`, `consumer`, `maxReceiveCount: 5`, `visibilityTimeoutSeconds: 60`,
`retention: "14d"`), `TASK_QUEUE_NAMES`, `TASK_DLQ_NAMES`, `taskQueueNameSchema`,
`isTaskQueue()`. Exported from `src/index.ts`.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Hyphenated queue names | SQS accepts only alphanumerics, hyphens and underscores; a dot is legal only as a trailing `.fifo`. The dotted names in the design notes were not creatable (proved by LocalStack in `inf-003`) | keep the dotted names and let the first producer fail |
| No recipient address in `sendEmailJobSchema` | the same PII rule that keeps emails out of the Kafka log applies to a 14-day queue: the worker resolves the address from `userId`/`orderId`/`cartId` | carry `to` "because SQS is private" |
| Required `idempotencyKey` | SQS is at-least-once; the key is what lets `notify.email_logs` drop the second delivery | rely on the visibility timeout |
| `queues.ts` separate from `topics.ts` | a task is a command for one worker; a topic is a fact for many consumers. Keeping them apart makes "tasks never go to Kafka" checkable in one test | one `messaging.ts` registry |
| Names as data (`TASK_QUEUES`) rather than three exported consts | the tests, the LocalStack hook and the Terraform all read one shape, and `TASK_QUEUE_NAMES`/`TASK_DLQ_NAMES` derive from it | `export const NOTIFY_QUEUE = "…"` × 3 |
| `reminder.dispatch` not declared | nothing ever produced to it; `cart.abandoned` + `notify-send-email` cover the flow | declare an unused queue for symmetry |

## Tests

`test/jobs.spec.ts` (new, 16 tests): a valid order job; a cart job keyed by user;
a job with **no** aggregate rejected; an embedded `to` rejected (PII);
`idempotencyKey` required; unknown template rejected; the import schema's mixed
scalars, `rowNumber: 0` rejected, `stockMode: "merge"` rejected, a nested object
rejected; a `resizeImageJobSchema` regression pinned as "1.8.0 adds, it does not
change"; and five registry invariants — exact names, `/^[A-Za-z0-9_-]{1,80}$/`
(no dots) for all six names, `-dlq` twin with 5/60/14d, task names absent from
`EVENT_TOPIC_NAMES`, and `isTaskQueue` accepting only its own names (explicitly
false for `reminder.dispatch`).

## Verification

- `pnpm typecheck` → 0 errors
- `pnpm test` → 5 files, **108 tests** green (16 new)
- `pnpm build` → clean
- `pnpm pack` → `ecom-contracts-1.8.0.tgz`; the tarball listing contains
  `dist/schemas/queues.js` and `.d.ts`
- `ecom-infra` repinned to the 1.8.0 tarball: `@ecom/contracts 1.7.0 → 1.8.0`,
  `provision-topics` reports `nothing to do`, `topics:smoke` 28/28,
  `verify-stack` 31/31

The CHANGELOG also backfilled **1.6.0** (catalog badges, product-card settings,
deprecated theme badges) and **1.7.0** (`cardPlacement`, `cardVariant`, gallery/grid
controls), which had shipped without entries, and `README.md` was refreshed to
1.8.0 with a task-queue section.

## Open

- `catalog-svc`, `cms-svc`, `search-svc` and `frontend/storefront` still pin
  `1.7.0`. Deliberate: 1.8.0 only adds schemas none of them import, and
  `resizeImageJobSchema` is unchanged. `ec-005` repins them in one train.
- Nothing enqueues yet: `notify-svc`, `import-svc` and the media worker do not
  exist, so `TASK_QUEUES` is a contract with no producer. The first producer must
  `safeParse` on enqueue and the worker on dequeue (stated in `9.Testing.md` §5).
