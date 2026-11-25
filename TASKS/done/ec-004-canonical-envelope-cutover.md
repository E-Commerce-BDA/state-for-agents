# ec-004 — contracts 2.0.0: canonical envelope cutover

- Repos: `ecom-contracts`, `ecom-messaging` + 11 adopters
- Phase: P5 · priority: P1 · kind: contract · transport: contracts
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `8ec4ba1` (contracts), `e01a57c` (messaging), then one per adopter:
  `795c69f` analytics, `ebfa5c6` auth, `934c4e4` cart, `665128d` catalog,
  `f0c5bc0` cms, `4b049ee` order, `3a1e98a` search, `b20d325` notify,
  `a97f91e` import, `ff45572` storefront, `17dfdb2` infra.

## What

Contracts 1.x carried three aliases for the event name (`type`, `topic`,
`eventType`) and `readEventEnvelope` silently defaulted `version` and
`idempotencyKey`. 2.0.0 makes all three canonical fields required and removes
the aliases and the dual-read fallback. Messaging 0.6.0 emits only the canonical
shape and widens its contracts peer range to `>=2.0.0 <3`.

All eleven adopters were repinned to the two locally packed tarballs in one
parallel wave. Fixtures and envelope assertions were updated to the canonical
shape; the tests that proved legacy aliases were *accepted* were replaced with
tests proving they are now *rejected*. No production code gained a fallback.

Stored 1.x outbox rows would be rejected by the 2.0.0 relay, so each service
that persists envelopes gained a one-time, idempotent backfill that rewrites
only pending rows: `type` comes from the row's own `event_type` column (NOT NULL
and already enforced by the `outbox_envelope_type_matches` CHECK), `version`
defaults to 1 and `idempotencyKey` to the event id, and both aliases are
dropped. Published/failed rows are never touched. Search needs no backfill —
`processed_events` stores only `(event_id, topic, processed_at)`, no envelope
body — and the storefront holds no stored envelopes at all.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Derive `type` from the outbox row's `event_type` column | It is NOT NULL, constrained to the service's topics, and already checked against the envelope, so a rewrite cannot make a row disagree with itself. On re-run the source is unchanged, so the `WHERE` predicate genuinely reaches zero rows. | Trust the legacy JSON alias — the first run deletes it, so a second run would have a different source of truth |
| Backfill pending rows instead of draining queues | The relay republishes stored envelopes verbatim; a 1.x row would be dead-lettered by every 2.0.0 consumer. Draining requires a live stack we do not have. | A runtime alias reader in each consumer — it would hide a producer that missed the cutover |
| Local tarballs, no tag or release | Exact pins are the polyrepo contract; every suite must be green before a release train. `ec-005` needs explicit human approval for tags and a GitHub Release. | Publish first and fix consumers after CI breaks |

## Verification

Serial waves: contracts 162 tests + typecheck green, tarball packed;
messaging 136 tests + typecheck + build green, tarball packed.

Consumer wave (all gates green in each repo): analytics 59 tests, auth 47,
cart 125, catalog 168, cms 206, order 89, search 162, notify 34, import 36,
storefront 1382 + lint 0 errors / 40 advisory + webpack build, infra 44 local
checks. Every tree is clean and every commit authored by the required identity.

Docs refreshed: `8.Versioning.md` current versions and both version histories,
the resolved cart pin-mismatch note, `1.Architecture.md` §7 envelope wording,
`2.Tech-Stack.md` and `3.Database-Schema.md` messaging version references.

## Follow-ups

- Every backfill SQL/CLI was reviewed and unit-tested but not executed against
  live Postgres/Mongo; e2e suites needing Postgres, Mongo, Kafka or LocalStack
  were skipped. Apply and verify the backfills in a real environment before
  the release train (`ec-005`).
- `ec-005` remains open: tags and GitHub Releases for the pinned versions need
  explicit approval. Nothing was pushed, tagged or published.
