# sf-084 — Added lib/theme/palette.ts and vars.ts with per-key precedence, reset-as-delete, locked contrast faces, --sf-* tokens plus legacy --color-* aliases and CSS mirrors; aligned admin BFF seam and 2.2.0 config envelope

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): d871032, 18c2486

## What

Added lib/theme/palette.ts and vars.ts with per-key precedence, reset-as-delete, locked contrast faces, --sf-* tokens plus legacy --color-* aliases and CSS mirrors; aligned admin BFF seam and 2.2.0 config envelope.

## Why

Deterministic inheritance and one default source; raw admin CSS would bypass clamps, contrast locks and preview parity. Rejected: scattered null fallbacks.

## Verification

Coordinator verified clean trees, author identity and gates in each repo:
contracts 184 tests + pack; cms 239 unit + 112 live e2e; storefront 1467
tests + lint/typecheck/build; admin 79 tests + lint/typecheck/build; docs
link and diff checks. No files were pushed or tagged by the agents.

## Follow-ups

- No live CMS document carrying the palette was available; contract-validated fixtures were used.
- --minicart-duration/-motion are emitted but have no CSS consumer yet.
