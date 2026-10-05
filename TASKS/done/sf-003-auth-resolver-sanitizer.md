# sf-003 — Auth settings resolver + sanitizer (done 2026-09-28)

> Reconstructed from session record 2026-10-05 (backfill).

## What

`lib/auth/resolveSettings.ts`: cascade page → shared → global → builtin;
clamps; stop-position fill (<2 stops → solid); allowlist HTML sanitizer
applied once server-side; unreadable scopes are misses, never errors.
The only file allowed `??` (reason header states it).

## How

- `mergeGroup` per-group spread honoring precedence; `isolateFromShared`
  makes forgot's own groups replace shared wholesale.
- `sanitizeAuthHtml`: strip script/style blocks, allowlist tags + attrs,
  `javascript:`/`on*` rejected.

## Decisions (+ rejected)

- Clamp/sanitize/fall-through over reject-and-error: theming must never
  break rendering. Rejected strict validation (wrong layer — CMS validates
  on write, resolver degrades on read).
- Sanitizer dependency-free (zero-new-deps rule); swap documented for
  cms-svc era if the allowlist outgrows it.

## Verification

9 resolver-unit tests, zero mocks; suite caught a real spec violation
(shared leaking into forgot) fixed before merge. `tsc` clean.
