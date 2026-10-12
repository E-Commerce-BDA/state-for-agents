# sf-034 — Dev CSS parse failure (done 2026-10-11)

User's Turbopack dev threw CssSyntaxError 800:1 Unexpected }.

## Finding
File on disk already valid (postcss PARSE-OK). Error matches the
PRE-repair revision (verified: old parses FAIL with Unexpected },
new parses OK). Root cause chain: stray `}` latent since sf-027 era
(webpack css-loader tolerated it, builds green) → sf-033 repair
removed it → dev server cached the dead revision.

## Fix
No code change (nothing broken on disk). User restarts dev server
(`rm -rf .next` if Turbopack holds the cache).

## Deliverable
css-structure.test.ts: postcss parse + brace-depth guard. This class
fails in CI now, not in dev weeks later.

## Commits
1. Guard test. 2+. Tracking close.

## Follow_ups
- None.
