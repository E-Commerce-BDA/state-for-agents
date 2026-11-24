# doc-005 — polyrepo comment cleanup, skill correction, and ADR refinement (done, 2026-11-24)

- Repos: all 10 comment-bearing repos + `Documentation` + `state-for-agents`
- Phase: P0 | priority: P2 | kind: docs | transport: docs
- Started: 2026-11-24 | Finished: 2026-11-24

## What

Two passes over every comment in the polyrepo. Pass 1 removed ~830 redundant
lines and created one categorized ADR file plus one-line `// ADR-*:` pointers.
Pass 2 used ten subagents, one per repo, each producing a full decision CSV from
a fresh extractor run; every table was spot-checked before any deletion was
applied. Pass 2 reviewed 1,810 blocks, deleted 435 blocks / 610 lines, and every
diff was deletion-only.

The skill itself was then corrected, because its classification reference taught
the wrong rule: it said the "Clamp once (1–10): a 0-cap would swallow every
push" comment was DELETE since the numbers are in the code. That one example
drove a mechanical first pass on storefront to cut 186 comments; 81 had to be
restored because their reason was invisible in the source. Final storefront
count: 105 deletes out of 576 blocks.

## Why

A comment that restates the signature, control flow, types or imports is bloat
even when it says "why" — AGENTS.md §3.4 already rules that way for `??`. But a
comment whose reason names a rejected alternative, an external constraint or a
non-local invariant is the only copy of that decision, so it stays even when the
action is obvious. The two-question test now states both halves.

One subagent per repo with disjoint file ownership was chosen because the apply
script deletes by line number: two agents writing one repo would invalidate each
other's ranges. Each agent submitted a decision table first, then applied only
after a spot-check.

Rejected: keyword- and length-based purges (already tried and rejected earlier);
mechanical "words appear beside the comment" matching; two agents per repo.

## How

- Extractor emits comment text plus the code before and after; every block gets
  a `delete`/`keep` decision and a one-line reason.
- `apply-decisions.py` validates whole comment ranges, refuses any range
  containing a code line, and skips directives, `///` refs and ADR pointers.
- It now normalizes decision casing — two agents wrote uppercase `DELETE` and
  got a silent no-op — warns on unknown values and hints on a zero apply.
- Per-block CSVs are persisted under `state-for-agents/comment-audit-pass2/`.

## Verification

- storefront: `tsc` clean, 1290 tests / 161 files, webpack build 39/39 pages.
- contracts 163, auth 29, cart 119, cms 163, analytics 20, catalog 165,
  messaging 136, order 75 tests — all green, all `tsc` clean.
- search-svc was red on four pre-existing `dlq` errors at the time; `srch-005`
  closed that afterwards.
- All ten comment commits are listed by repo in `STATUS.md` §7 and in the
  `comment-audit-pass2` summary.

## Follow-ups

- `ADR-comments-ratchet` is written but not implemented: no comment counter or
  CI gate exists yet.
- Live-stack verification of service-backed e2e remains blocked (cms-svc :4050,
  Mongo :27018).
