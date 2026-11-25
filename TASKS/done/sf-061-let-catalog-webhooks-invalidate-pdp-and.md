# sf-061 — Let catalog webhooks invalidate PDP and listing caches.

- Repos: storefront-ui
- Commit(s): a41a96b
- Closed: 2026-11-26

## What

Let catalog webhooks invalidate PDP and listing caches.

## Why

Time-based revalidation alone leaves stale prices too long.

Rejected: Polling catalog on every render.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- The catalog-svc webhook caller is still outside this repo.
