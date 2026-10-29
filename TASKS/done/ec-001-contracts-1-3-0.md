# ec-001 — Contracts 1.3.0 canonical envelope (done, 2026-10-29)

## What

Add a canonical event envelope with a dual-read/dual-write window so producers
and consumers can migrate without a flag day. `type` becomes the event name and
Kafka topic; legacy `topic`/`eventType` remain readable until 2.0.0.

## How

- `ecom-contracts/src/schemas/events.ts` — added optional `type`; made
  `topic`/`eventType` legacy-optional; require at least one identifier; added
  `canonicalEventEnvelopeSchema` and `readEventEnvelope()`.
- `ecom-contracts/test/contracts.spec.ts` — added eight tests: canonical,
  legacy CMS mismatch, topic-only/eventType-only, missing identifier,
  dual-write drift, agreeing dual-write, canonical required fields, and
  unknown fields.
- `ecom-contracts/package.json` — bumped to `1.3.0`.
- `ecom-contracts/CHANGELOG.md` — added 1.3.0 and the missing 1.2.0 entry.
- `ecom-contracts/VERSIONING.md` — documented the 1.3.0/2.0.0 transition.
- Local `ecom-contracts-1.3.0.tgz` produced; ignored by git, not published.

## Decisions

- **`type` is both the event name and the Kafka topic** — removes the
  `topic`/`eventType` drift that publishes `cms.updated` on `cms.events`.
  Rejected: keep separate fields plus a mapping table.
- **Legacy fields stay optional in 1.3.0** — existing pinned consumers keep
  working while producers dual-write. Rejected: jump straight to 2.0.0 and
  break every consumer at once.
- **Schema rejects dual-write drift when `type` is present, but accepts the
  legacy CMS mismatch when `type` is absent** — new producers fail fast, old
  CMS messages remain readable. Rejected: reject every mismatch (breaks the
  current CMS wire shape) or allow every mismatch (silent drift).
- **`readEventEnvelope()` defaults `version` to 1 and `idempotencyKey` to
  `id`** — legacy messages lack both; the event id is the deterministic
  fallback. Rejected: require both fields before producers migrate.

## Verification

- `pnpm test`: 3 files, 54 tests green, including 8 new envelope tests.
- `pnpm typecheck`: clean.
- `pnpm build`: clean.
- `pnpm pack`: `@ecom/contracts@1.3.0` tarball produced.
- Commit `4383b26` in `ecom-contracts`; no push, tag, or release.
- Follow-ups: `ec-002` missing event payloads, `ec-003` SQS job schemas,
  `ec-004` 2.0.0 cutover, `ec-005` release train.
