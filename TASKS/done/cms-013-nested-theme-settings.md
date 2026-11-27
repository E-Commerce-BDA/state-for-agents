# cms-013 — Admin PUT now validates and persists every nested 2.2.0 theme group; public GET returns the stored theme with version/configured and existing side effects

- Repo: `cms-svc`
- Verified: 2026-11-27
- Commit(s): 309389b

## What

Admin PUT now validates and persists every nested 2.2.0 theme group; public GET returns the stored theme with version/configured and existing side effects.

## Why

The service already validated with themeSettingsSchema; with 2.2.0 no normalisation code was needed. Rejected: flattening nested groups in the service.

## Verification

Coordinator verified clean trees, author identity and gates in each repo:
contracts 184 tests + pack; cms 239 unit + 112 live e2e; storefront 1467
tests + lint/typecheck/build; admin 79 tests + lint/typecheck/build; docs
link and diff checks. No files were pushed or tagged by the agents.

## Follow-ups

- Two opt-in e2e suites (LocalStack SQS, live Kafka) remain skipped; unrelated.
