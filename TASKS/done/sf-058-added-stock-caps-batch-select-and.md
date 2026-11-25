# sf-058 — Added stock caps, batch select and checkout chrome.

- Repos: storefront-ui
- Commit(s): 6ecd401
- Closed: 2026-11-26

## What

Added stock caps, batch select and checkout chrome.

## Why

A pure ceiling keeps the stepper and the write consistent when catalog is available.

Rejected: Clamping only in the UI and sending an uncapped write.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Shipping method is UI state only; order-svc has no shippingMethod field.
