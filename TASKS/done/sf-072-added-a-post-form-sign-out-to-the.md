# sf-072 — Added a POST-form sign-out to the shell account menu.

- Repos: storefront-ui
- Commit(s): 708d379
- Closed: 2026-11-26

## What

Added a POST-form sign-out to the shell account menu.

## Why

The logout route is POST-only by design; a GET link would be cross-site unsafe.

Rejected: A client-side token clear leaving HttpOnly cookies intact.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups


