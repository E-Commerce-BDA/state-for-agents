# sf-008 — AGENTS.md constitution + Learning Mode (done 2026-09-30 / 2026-10-02)

> Reconstructed from session record 2026-10-05 (backfill).

## What

`frontend/storefront/AGENTS.md` v1.0: identity, structure gradient
(smart → pure → dumb), consolidated dumb-component guide (from
button/tooltip/icons docs), mandatory test trio, construct rules
(reason-required vs hard-banned), workflow (docs-first, one-commit,
merge gate). Later: agent-bootstrap pointer + Learning Mode §7
(always-on, explicit skip phrase). Cross-repo philosophy duplicated at
`state-for-agents/LEARNING.md` (single home) with per-repo pointer.

## Decisions (+ rejected)

- `??`/fallbacks reason-required, not banned (user correction):
  single-place defaults + bloat test. Rejected strict bans (compliance
  over engineering) AND anything-goes (bloat). Hard bans kept for the
  four provable-bug classes.
- Constitution per repo, memory cross-repo; conflict rule: repo wins
  locally, amendment filed same turn.

## Verification

Constitution cited by every subsequent file placement; committed
(`Adding agents.md` + amendment commits), pushed to `main`.
