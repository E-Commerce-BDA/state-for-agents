# sf-073 — Count CMS fallback and rejected revalidations as metrics.

- Repos: storefront-ui
- Commit(s): 196d1ef
- Closed: 2026-11-26

## What

Count CMS fallback and rejected revalidations as metrics.

## Why

A logged fallback is not a signal a dashboard can read.

Rejected: More console logging.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups


