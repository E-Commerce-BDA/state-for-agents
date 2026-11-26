# inf-006 — replay the accumulated order.created dead letters

- Repo: `ecom-infra`
- Phase: P5 · priority: P1 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `67e5a31` (tool), `1090a99` (the actual drain)
- Verified: **2026-11-26 against the live stack, with explicit user approval for a destructive operation**

## What

A bounded, reconciling replay tool for `order.created.dlq` with a dry-run
default and a four-consumer guard (all on messaging 0.6.0 with
`retryBudgetMs = 20_000`).

## Verification (live)

Approved command:

```powershell
pnpm dlq:replay -- --execute --acknowledge-drain --discard-legacy --max-messages 10000
```

- Read **3,679** records: canonical 3, legacy 3,666, other 10, duplicateIds 1,
  replayable 2.
- `replayed 2`, `duplicate 1`, `skipped 3,676`, `parked 0`, `committed 3,679`;
  reconciliation **PASS**, exit 0.
- Replay-group offsets equal log end on every partition (1228 / 1228 / 1223,
  lag 0); a follow-up `pnpm dlq:replay -- --dry-run --from-replay-offset`
  read **0** records.
- After restarting all four consumers and running the suites, DLQ end offsets
  were unchanged and cart/catalog/notify/analytics all showed lag 0 on
  `order.created` — no new dead letters from the same offsets.
- Gates: `pnpm test:local` 59/59; all four `check:*` scripts green;
  `node --check` clean.

## Caveats

The Kafka log itself was **not deleted**: end offsets remain 3,679 until topic
retention expires. "Drained" means the logical backlog is zero — offsets are
committed past every record and no consumer has lag. Legacy records were
skipped/discarded by the tool under the user's explicit approval, not
republished. No DLQ deletion happened outside the tool. One failed first
attempt (Kafka reset CLI expects `topic:partition`, not `--partition`) was
fixed inside the tool before the successful run.

## Follow-ups

- None.
