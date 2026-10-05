# sf-002 — Auth settings vocabulary + builtin fallbacks (done 2026-09-27)

> Reconstructed from session record 2026-10-05 (backfill).

## What

`lib/auth/settings.ts`: admin-facing partial types (absent = inherit),
all-required resolved types, `DEFAULT_AUTH_SETTINGS` (today's look = final
fallback), `AUTH_LIMITS`, per-page form titles. Shared set for
signin+signup, separate style for forgot.

## How

- Mirrored `lib/cms/buttonAnimation.ts` three-tier shape.
- Discriminated-union panel gradient (angle linear-only by construction;
  CSS 0-toward-top convention documented once on the type).

## Decisions (+ rejected)

- Per-page `pages` key kept minimal (layout/side + forgot style) over a
  fully per-page model: "same everywhere" locked, fewer fields today.
- Hex literals legal only in `DEFAULT_*` — single home for literals.

## Verification

`tsc` clean; consumed by sf-003 resolver tests. No logic in file
(grep: no `??`, no fetch, no React).
