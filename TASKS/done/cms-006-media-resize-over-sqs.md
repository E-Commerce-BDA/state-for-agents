# cms-006 — media resize over SQS instead of Kafka (done, 2026-11-01)

## What

An upload published a `media.tasks` record on the Kafka bus and nothing consumed it:
`media.tasks` was never an `EVENT_TOPIC`, and a command for one worker had no business
on the domain-event bus. cms-006 replaces that publish with an SQS task on
`media-resize-image` and adds the worker that actually produces the renditions, so an
upload now ends with `width`, `height` and a variant manifest on the media document.

The task was under-scoped in the tracker: `@ecom/messaging` 0.3.0 had no task-queue
code at all (no port, no producer, no worker) and `@ecom/contracts` had no envelope to
carry an idempotency key. Both landed first, as their own commits: contracts `1.11.0`
(`taskMessageSchema`) and messaging `0.4.0` (`TaskQueuePort`, `SqsTaskQueue`,
`SqsTaskWorker`, `createSqsTaskModule`).

## How

- `ecom-contracts/src/schemas/tasks.ts` (new) — `taskMessageSchema`:
  `{ id, queue, type, idempotencyKey, enqueuedAt, payload }`, strict, exported with the
  rest of the package; `test/tasks.spec.ts` covers it.
- `ecom-messaging/src/tasks/` (new) — `task-queue.port.ts` (`TaskQueuePort`,
  `TaskWorkerPort`, both taking a `TaskQueue` rather than a string so `TASK_QUEUES`
  stays the only source of names), `sqs-task-queue.ts` (`SendMessage` with a
  `MessageAttributes.idempotencyKey`, body validated by `taskMessageSchema` before
  send), `sqs-task-worker.ts` (`ReceiveMessage` with `waitTimeSeconds: 20`,
  `maxNumberOfMessages: 10`, visibility from `TASK_QUEUES`, delete only after the
  handler resolves, `ApproximateReceiveCount` logged), `nest/tasks.module.ts`
  (`createSqsTaskModule`).
- `cms-svc/package.json` — repinned to `contracts-1.11.0.tgz` and
  `messaging-0.4.0.tgz`, plus `sharp`.
- `cms-svc/src/events/` — deleted. `EventsService`, both event buses and the module are
  gone: this service has no Kafka producer and no Kafka consumer left.
- `cms-svc/src/media/media-tasks.publisher.ts` (new) — builds the task message
  (`type: 'media.resize-image'`, `idempotencyKey: mediaId`, `widths`/`formats`) and
  enqueues it on `TASK_QUEUES.mediaResizeImage`. Queue disabled ⇒ one debug line;
  enqueue failure ⇒ one error line, because by then the bytes are stored and the media
  row is committed, so a 500 would report a failure that did not happen.
- `cms-svc/src/media/media-resize.service.ts` (new) — fetches the original through
  `StoragePort`, reads `width`/`height` with `sharp().metadata()`, writes each
  `widths × formats` variant to `media/<yyyy>/<mm>/<uuid>-<w>.<ext>`, and persists
  `variants: [{ width, format, key, url, bytes }]` with a single `$set`.
- `cms-svc/src/media/media-resize.module.ts` (new) — publishes the resize handler as a
  token for `createSqsTaskModule` (a dynamic module cannot see this module's providers)
  and provides the publisher.
- `cms-svc/src/config/env.validation.ts`, `.env.example` — `SQS_TASKS_ENABLED`
  (default `false` in development, `true` in production), `AWS_REGION`,
  `AWS_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.
- Tests: `media-tasks.publisher.spec.ts` (enqueue called once with the right queue and
  key, disabled path silent, failure does not throw), `media-resize.service.spec.ts`
  (metadata + variants written, replay is a no-op, widths above the source dropped),
  `test/media-resize.e2e-spec.ts` (LocalStack-gated, skips with a printed reason),
  `test/media.e2e-spec.ts` now asserts **no** Kafka publish.

## Decisions (+ one rejected alternative each)

1. **A task, not an event.** `media.tasks` had no consumer and no other service will
   ever care; putting it on SQS with an idempotency key makes it a job with an owner.
   Rejected: keep `media.tasks` on Kafka and just add a consumer — it would still be a
   point-to-point command disguised as a domain event.
2. **The worker lives in cms-svc.** One queue does not justify a tenth service with its
   own deploy, database and credential set. Rejected: a `media-svc`.
3. **The DLQ is the queue's redrive policy.** Terraform and the LocalStack init already
   declare `media-resize-image-dlq` with `maxReceiveCount 5`; a worker that published
   its own DLQ records would be a second source for one policy. Rejected: hand-rolling
   a DLQ publisher in `SqsTaskWorker`.
4. **Idempotent by construction.** The manifest is written once with a single `$set`,
   an existing width/format pair is reused, and a width above the source is dropped
   rather than upscaled — so a re-delivered job rewrites identical values. Rejected:
   upsert each variant separately, where a partial failure leaves half a manifest.
5. **A failed enqueue does not fail the upload.** The response would be a 500 for work
   that already succeeded, and re-enqueuing by media id is a repair. Rejected:
   transactional enqueue (SQS is not in the Mongo transaction, so the failure mode
   would just move).
6. **`@ecom/messaging/nest/tasks`, not the `/nest` barrel.** The barrel also
   re-exports the Kafka consumer surface, which would force `@nestjs/microservices` on
   a service with no consumer. Rejected: one wide barrel and a dependency this service
   will never call.

## Verification

| Check | Result |
|---|---|
| `ecom-contracts` `pnpm test` | 129 passed (6 files) |
| `ecom-contracts` `pnpm pack` | `ecom-contracts-1.11.0.tgz` |
| `ecom-messaging` `pnpm test` | 125 passed (12 files), 25 of them the new task specs |
| `ecom-messaging` `pnpm pack` | `ecom-messaging-0.4.0.tgz` |
| `cms-svc` `pnpm test` | 149 passed (22 files) |
| `cms-svc` `media-tasks.publisher.spec.ts` | enqueue once per upload with `media-resize-image` + `idempotencyKey = mediaId`, disabled queue enqueues nothing, enqueue failure is logged and the upload still succeeds |
| `cms-svc` `media-resize.service.spec.ts` | metadata + variants in one `$set`, replay is a no-op, oversize widths dropped |
| `cms-svc` `test/media-resize.e2e-spec.ts` | green against real LocalStack (`AWS_ENDPOINT_URL=http://localhost:4566`): upload → message → worker → variants on the document; skips with a printed reason without it |
| `cms-svc` `test/media.e2e-spec.ts` | asserts the upload publishes nothing to Kafka |
| `cms-svc` `pnpm test:e2e` | 87 passed, 4 skipped (9 files passed, 2 skipped) |
| `cms-svc` `pnpm lint` / `pnpm build` / `pnpm typecheck` | 0/0 on 100 files / clean / exit 0 |
| commit | `ecom-contracts` `7fdfdc2`, `ecom-messaging` `c76acbe`, `cms-svc` `fc2d646` |

## Open

- `SQS_TASKS_ENABLED` defaults to `false` in development and test, so an upload on a
  box without LocalStack succeeds and simply has no renditions.
- `ecom-infra` compose has no profile that starts LocalStack; the queue e2e is started
  explicitly by hand.
- No variant garbage collection: deleting a media row leaves its renditions in storage.
