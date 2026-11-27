# cms-014 — CMS navigation service validates and round-trips 2.2.0 mega-menu groups/columns/promos with safe href checks and specific 400 codes

- Repo: `cms-svc`
- Verified: 2026-11-27
- Commit(s): e1bcf02

## What

CMS navigation service validates and round-trips 2.2.0 mega-menu groups/columns/promos with safe href checks and specific 400 codes.

## Why

Contract-owned limits keep admin, CMS and storefront aligned; a CMS-side helper would duplicate the rule. Rejected: local limit copy.

## Verification

Coordinator verified clean trees, author identity and gates. cms: 267 unit
and 117 live e2e; admin: 103 tests, lint/typecheck/build green.

## Follow-ups

- Storefront resolveNav pass-through was assigned to sf-089 follow-up.
- Two opt-in suites (LocalStack SQS, live Kafka) stayed skipped.
