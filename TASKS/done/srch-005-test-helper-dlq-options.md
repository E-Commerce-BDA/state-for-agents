# srch-005 — fix the four dlq type errors left by messaging 0.5.0 (done, 2026-11-24)

- Repos: `search-svc`
- Phase: P0 | priority: P1 | kind: bug | transport: kafka-consumer
- Started: 2026-11-24 | Finished: 2026-11-24

## What

`npx tsc --noEmit` reported four errors in
`test/search-consumer.controller.spec.ts`: two empty default overrides typed as
the full `KafkaEventHandlerOptions` (which requires `dlq`), one call passing only
`translateError`, and a TS2783 duplicate-property warning because the test's own
`dlq` was followed by a spread that could overwrite it.

Added a local `HandlerOverrides = Partial<Omit<KafkaEventHandlerOptions, 'dlq'>>`
and moved the spread to the first entry of the constructor call. Typecheck is
clean and 142 tests pass across 20 files.

## Why

The shared contract must keep `dlq` required for every service — messaging 0.5.0
made it required on purpose so a consumer cannot silently lose its dead-letter
sink. Only the test helper may vary the other knobs.

The suite's DLQ publisher is the object whose mock producer the `sentTopic()` and
`sentRecord()` assertions inspect, so a caller must not be able to replace it.
Spreading first also removes the TS2783 warning instead of suppressing it.

Rejected: adding `dlq` at each of the four call sites (repeats publisher setup
and keeps the overwrite warning); `as any` or making `dlq` optional in the shared
package (weakens messaging 0.5.0 everywhere).

## How

- One new type alias and two signature changes in the spec.
- One comment recording the invariant the type alone cannot prove.
- Commit `7af63fe` in `search-svc`.

## Verification

- `npx tsc --noEmit` exit 0.
- `pnpm test`: 20 files, 142 tests passed. The `ECONNREFUSED` and Kafka warnings
  in the log are failure-path fixtures, not failures.

## Follow-ups

None.
