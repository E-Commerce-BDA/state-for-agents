# sf-096 — Storefront preview honors ?preview tokens with no-store upstream fetches, emits the 2.2.0 config envelope, and consumes the admin's versioned draft postMessage with origin/shape validation and frame-ancestors CSP

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): c5b9f93, 99da49d

## What

Storefront preview honors ?preview tokens with no-store upstream fetches, emits the 2.2.0 config envelope, and consumes the admin's versioned draft postMessage with origin/shape validation and frame-ancestors CSP.

## Why

Preview token and draft must affect only the upstream fetch and an ephemeral per-frame patch; leaking them to cache/islands would break privacy and published state. Rejected: raw CSS patching.

## Verification

Coordinator verified clean trees, author identity and gates. Storefront:
249 files / 1678 tests, lint 0 errors, tsc and webpack green. Admin: 123
tests, lint 0 errors, typecheck and build green.

## Follow-ups

- Navigation draft patches are accepted but do not repaint nav chrome in this pass.
- No live admin-iframe browser run; contract/unit coverage only.
