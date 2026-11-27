# doc-008 — Documented the layered token architecture, AA locks, inheritance formula, admin/storefront token separation, no-new-useState rule and planned component artifacts

- Repo: `Documentation`
- Verified: 2026-11-27
- Commit(s): f08e72a

## What

Documented the layered token architecture, AA locks, inheritance formula, admin/storefront token separation, no-new-useState rule and planned component artifacts.

## Why

Docs-first for new patterns; a conversation-only decision would drift. Rejected: relying on memory.

## Verification

Coordinator verified clean trees, author identity and gates in each repo:
contracts 184 tests + pack; cms 239 unit + 112 live e2e; storefront 1467
tests + lint/typecheck/build; admin 79 tests + lint/typecheck/build; docs
link and diff checks. No files were pushed or tagged by the agents.

## Follow-ups

- None.
