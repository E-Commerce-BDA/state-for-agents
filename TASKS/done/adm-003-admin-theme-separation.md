# adm-003 — Renamed admin chrome vars to --adm-*, removed merchant overrides from admin chrome, fixed BFF paths and config version, and rewrote the theme editor to the nested 2.2.0 contract

- Repo: `admin-app`
- Verified: 2026-11-27
- Commit(s): cda1f53

## What

Renamed admin chrome vars to --adm-*, removed merchant overrides from admin chrome, fixed BFF paths and config version, and rewrote the theme editor to the nested 2.2.0 contract.

## Why

Admin actions must stay ink-based and the tool that edits merchant theme must not be re-skinned by it. Rejected: reusing --sf-* in both apps.

## Verification

Coordinator verified clean trees, author identity and gates in each repo:
contracts 184 tests + pack; cms 239 unit + 112 live e2e; storefront 1467
tests + lint/typecheck/build; admin 79 tests + lint/typecheck/build; docs
link and diff checks. No files were pushed or tagged by the agents.

## Follow-ups

- Component-group prefill uses explicit resolved-var mapping; unmapped groups start blank.
- No live cross-repo E2E was run.
