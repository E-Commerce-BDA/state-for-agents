# tst-002 — failure injection and P0 regression gate

- Repo: `ecom-infra` (gate); fix in `analytics-svc`
- Phase: P5 · priority: P0 · kind: test
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `caa5617` (gate), `3d67b84` (analytics reclaim fix)
- Verified: **2026-11-26 against the live stack**

## What

`pnpm e2e:faults` injects Kafka down, duplicate delivery, malformed payload,
Redis down and DB failure after capture, then checks that all faults are
restored. It exits non-zero on a genuine service defect rather than hiding it
behind a harness skip.

The first live run exposed a real analytics-svc bug: on a redelivered event the
claim insert (`_id: eventId`) failed with duplicate key `11000` inside a Mongo
transaction. The code swallowed the error and returned "duplicate", but Mongo
had already aborted the transaction; the driver then retried the poisoned
transaction for ~2 minutes, burning the consumer's retry ladder and dead-lettering
the duplicate. The partition stayed held, so the recovery event never arrived
inside the gate's 45-second window. The fix calls `session.abortTransaction()`
on code `11000` so `withTransaction` exits cleanly. It also removes the invalid
`unique` `_id` index declaration, adds an idempotent repair CLI, and adds
`class-validator`/`class-transformer` used by `ValidationPipe`.

## Verification (live)

- First run: 6 PASS / 1 FAIL — analytics did not reclaim after broker restart,
  reproduced twice.
- After `3d67b84`: **7 PASS / 0 FAIL**, plus `preflight: stack healthy` PASS,
  process exit 0. All four consumer groups claimed the recovered event;
  duplicate delivery caused one side effect; malformed payload landed in
  `order.created.dlq` with active groups advancing; Redis-down checkout returned
  503 `IDEMPOTENCY_UNAVAILABLE` with zero new orders; DB failure after capture
  left payments 335→335 and zero orphan captured payments. All faults restored.
- Analytics boot log clean: no shim line, no aborted-transaction retry, no
  duplicate DLQ writes.
- Gates: analytics typecheck, 61 tests, lint and build green; infra local gates
  53/53 with all static checks green.

## Caveats

- A real payment-provider capture failure, network partitions, a real AWS SQS
  outage and durable DB crash/recovery are not injectable in this environment.
- The index-repair CLI was a verified no-op on the live DB (no bad index
  present); only its unit tests exercise the repair path.
- `pnpm test:e2e` in analytics-svc was not run (not a requested gate).
- The first post-fix gate attempt hit `EADDRINUSE` on port 4040 from a leftover
  process; ports were freed and the rerun passed.

## Follow-ups

- None for the gate itself. The separate DLQ backlog drain is `inf-006`.
