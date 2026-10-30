# inf-002 — declarative Kafka topic and DLQ provisioning

- Repo: `ecom-infra` (+ root `pnpm-workspace.yaml`)
- Phase: P1 · priority: P0 · kind: infra · transport: infra
- Started: 2026-10-30 · Finished: 2026-10-30

## What

The broker starts with `KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'`, so before this
task an event could not be published at all: nothing created a topic. The list
now lives in `EVENT_TOPICS` (`@ecom/contracts/src/schemas/topics.ts`) and
`scripts/provision-topics.mjs` is the only writer.

`pnpm topics:provision` computes the delta and applies it per topic:

| Situation | Action |
|---|---|
| topic absent | create with the registry's partition count, retention and `min.insync.replicas=1` |
| live partitions < registry | `--alter --add-partitions` up to the registry value |
| live `retention.ms` differs | `--alter --config retention.ms=<ms>` |
| live partitions > registry | **conflict**, reported and left alone — Kafka cannot remove partitions |
| topic live but not in the registry | warned, never deleted |

Result: **22 topics** (11 events + 11 `.dlq` twins). A second run prints
`nothing to do: 22 topics already match the registry`.

## Bugs found on the way

1. **`--config retention.ms=…` as a single argv element** →
   `joptsimple.UnrecognizedOptionException`. `kafka-topics.sh` needs the flag and
   the value as two argv entries, so `baseConfig()` returns
   `['--config', 'retention.ms=…', '--config', 'cleanup.policy=delete', …]`.
2. **`kafka-console-producer.sh` exits 0 on a rejected produce.** It logs
   `UNKNOWN_TOPIC_OR_PARTITION` to stderr and reports success, so a naive
   `execFileSync` check proves nothing. `scripts/kafka.mjs` now exposes
   `kafkaCapture()` (spawnSync → `{code, output}`) next to `kafka()`, and the
   auto-create check asserts on the log text.

## Smoke test

`pnpm topics:smoke` → **28/28**:

- registry shape: partitions and `retention.ms` for all 22 topics;
- keyed partitioning: a throwaway `smoke.probe` topic with 3 partitions receives
  30 keys and all three partitions are hit, then the topic is deleted;
- auto-create off: producing to `ecom.autocreate.probe` is rejected with
  `UNKNOWN_TOPIC_OR_PARTITION` and the topic is not created;
- no strays: the broker holds exactly the 22 declared topics.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Registry-driven provisioning, not a topic list in compose | one source of truth; the contract package already answers "who publishes/consumes this" | a second list in the infra repo that drifts |
| Raise partitions, never lower them | Kafka cannot lower them, and silently ignoring the difference hides a real drift | fail the whole run on any mismatch |
| Warn about unregistered live topics instead of deleting them | a stray topic may hold a producer's data while a contract is being added | `--delete` anything not in the registry |
| Keep `min.insync.replicas=1` | single broker; `acks=all` with ISR 2 would block every write | copy the production value into the local stack |

## Open

- `provision-topics.mjs` is not run by `compose up`; it is a deliberate second
  step (`pnpm topics:provision`) so a wiped volume cannot silently recreate a
  half-configured broker.
- The local `smoke.probe` topic is created and deleted inside the test; if the
  test dies between the two, the next run reports it as a stray and the operator
  deletes it manually.
