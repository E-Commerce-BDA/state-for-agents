# inf-008 — retention sweeping for outbox and processed_events

- Repo: `ecom-infra`
- Phase: P5 · priority: P1 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `8b3746b` (sweep/config/tests), `7451d54` (live DELETE fix)
- Verified: **2026-11-26 against the live stack**

## What

One scheduled sweep prunes rows older than the topic retention across every
store: auth/cart/catalog/order/import outboxes, four `processed_events` tables
and Mongo `cms_outbox`. The sweep is driven by `retention/config.mjs` and
exposes `pnpm retention:sweep`. A live-only bug — the generated DELETE used an
`id` column on `processed_events`, which has no such column — was fixed in
`7451d54`.

## Verification (live)

- A backdated row was pruned and a recent row survived in **all eight live
  stores**, including Mongo `cms_outbox`.
- A second sweep deleted **zero** rows everywhere — idempotency observed, not
  just reasoned.
- Gates: `pnpm test:local` 53/53; all four `check:*` scripts green;
  `node --check` clean.

## Follow-ups

- None.
