# anl-005 — cart.abandoned docs and payload now agree on the PII rule.

- Repos: analytics-svc
- Commit(s): 728b7cf
- Closed: 2026-11-26

## What

cart.abandoned docs and payload now agree on the PII rule.

## Why

Events stay PII-minimal; addresses come from au-005's internal lookup.

Rejected: Adding the email field back to the event.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- §7.2 example still lists unrelated stale fields for a docs pass.
