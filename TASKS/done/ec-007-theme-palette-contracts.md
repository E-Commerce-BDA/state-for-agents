# ec-007 — Added themePaletteSchema, component groups, resolved theme/var schemas, CMS-backed mega-menu navigation and storefrontConfigResponseSchema in contracts 2.2.0

- Repo: `ecom-contracts`
- Verified: 2026-11-27
- Commit(s): 4cb5ad0

## What

Added themePaletteSchema, component groups, resolved theme/var schemas, CMS-backed mega-menu navigation and storefrontConfigResponseSchema in contracts 2.2.0.

## Why

The strict 2.1.0 contract rejected the admin's flat theme fields; an additive typed palette keeps every existing reader valid. Rejected: raw admin CSS variables.

## Verification

Coordinator verified clean trees, author identity and gates in each repo:
contracts 184 tests + pack; cms 239 unit + 112 live e2e; storefront 1467
tests + lint/typecheck/build; admin 79 tests + lint/typecheck/build; docs
link and diff checks. No files were pushed or tagged by the agents.

## Follow-ups

- Downstream repins completed in cms-svc, storefront, admin-app and ecom-infra.
