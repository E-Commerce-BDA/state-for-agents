# sf-006 — Primitive seams (done 2026-09-29)

> Reconstructed from session record 2026-10-05 (backfill).

## What

- `ui/Input`: radius widened `number|string` (var passthrough); focus
  border/shadow + placeholder via `--auth-*` vars with current-value
  fallbacks; `rightIconInteractive` renders operable adornments without
  the decorative `aria-hidden` wrapper. (Placeholder tone subtle change
  aligned to Textarea precedent — noted, accepted.)
- `ui/icons`: 27th icon `eye-off` (password toggle must be perceivable;
  same-stroke sibling); `icons.md` updated (26→27); `it.each(ICON_NAMES)`
  test auto-extended coverage.

## Decisions (+ rejected)

- Minimal backward-compatible widening over new props: zero behavior
  change outside auth scope. Rejected a parallel "themed input" component
  (duplication) and `!important` overrides (bloat rule).

## Verification

Full suite stayed green (icon set test covers the new key); `tsc` clean.
