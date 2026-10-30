# doc-002 — testing matrix for Kafka, SQS, outbox and DLQ

- Repo: `Documentation` (+ `0.Project-Overview.md`, `5.Features.md`, `6.Admin-Panel.md`)
- Phase: P1 · priority: P0 · kind: docs · transport: docs
- Started: 2026-10-30 · Finished: 2026-10-30

## What

`9.Testing.md` described behaviour but never said how to get a stack that can
prove it, and its "Event Log + Task Queue Matrix" was one table that mixed
transport semantics with cost. Replaced with four sections:

- **§4 Local Harness: Bring-Up and Test Commands** — `pnpm up` / `pnpm verify`
  (31 checks) for the stack, `pnpm topics:provision` + `pnpm topics:smoke`
  (28 checks) for Kafka, the LocalStack ready-hook (plus how to rerun it and the
  Terraform apply/destroy against LocalStack) for SQS, and a per-repo command
  table naming the database each `test:e2e` needs.
- **§5.1 Concern matrix** — producer outbox, consumer dedupe, ordering,
  failure/DLQ, replay, fan-out, cost hygiene, with the Kafka assertion and the
  SQS assertion side by side. The SQS column now says explicitly that tasks are
  **not** replayable.
- **§5.2 P0 regression cases** — ten cases with the file that proves each.
- **§8 Test Data + Environments** — one compose stack, LocalStack for SQS, same
  fixtures everywhere.

Sections 6–9 were renumbered; the doc header moved to 2026-10-30.

## Stale claims removed

The acceptance criterion "no stale SNS/SQS event claims remain" found three:

| File | Was | Now |
|---|---|---|
| `0.Project-Overview.md` §4.2 | `@aws-sdk/client-sns` + `@aws-sdk/client-sqs` behind `ITaskQueue` | `@aws-sdk/client-sqs` only, with "No SNS: events never travel through SNS→SQS" |
| `5.Features.md` header | "Kafka local / SNS→SQS AWS, `1.Architecture.md §6.5`" | "Kafka in every environment"; tasks via SQS; no SNS→SQS path |
| `6.Admin-Panel.md` §6 pipeline | same phrase on the `cms.updated` line | "Kafka in every environment, see `1.Architecture.md §6`" |

`0.Project-Overview.md` also had two `ecom-contracts/src/events/` / `src/jobs/`
paths in §11.4; they are `src/schemas/events.ts` and `src/schemas/jobs.ts`.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Harness commands in the testing doc, not only in `ecom-infra/README.md` | a test plan that assumes an unstated environment is not a test plan | link to the infra repo and hope |
| Per-transport matrix with the SQS column saying "not replayable" | the most expensive misunderstanding is assuming a task can be replayed like an event | one table with a "replay" row that implies both transports support it |
| P0 list names the proving file | "we test the DLQ" is unverifiable; `search-svc/test/kafka-event-consumer.spec.ts` is not | a prose list of concerns |
| Name the Mongo `directConnection=true` requirement in the command table | the failure mode (`ENOTFOUND mongo`) looks like a broken compose stack | document it only in `services/cms.md` |

## Open

- `notify-svc` does not exist, so P0-5 (task DLQ + dedupe) has no proving file
  yet; the row says so instead of pointing at a file that does not exist.
- k6 thresholds and Playwright suites are still specified, not implemented;
  §7 stays aspirational until those repos have scripts.
