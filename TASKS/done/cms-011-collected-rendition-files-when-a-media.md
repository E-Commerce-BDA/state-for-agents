# cms-011 — Collected rendition files when a media row is deleted.

- Repos: cms-svc
- Commit(s): 07e2c22
- Closed: 2026-11-26

## What

Collected rendition files when a media row is deleted.

## Why

Deletion is at-least-once, so a missing file must be success.

Rejected: A nightly sweep with no ownership signal.

## Verification

Local gates were rerun by the coordinator: typecheck, unit tests, lint and build
green in the owning repo. Anything needing a live stack is listed below rather
than claimed.

## Follow-ups

- Mongo e2e needs a live stack.
