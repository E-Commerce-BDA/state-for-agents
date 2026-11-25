# sf-057 — Carried the cart coupon into the checkout summary.

- Repos: storefront-ui
- Commit(s): 3b80316
- Closed: 2026-11-26

## What

Carried the cart coupon into the checkout summary.

## Why

A coupon accepted in the cart must appear where the shopper pays.

Rejected: A second coupon lookup in the checkout island.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups


