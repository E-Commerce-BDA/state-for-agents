# sf-018 — Sheet slide animation, per-variant motion (done 2026-10-10)

> Owner: agent. Scope: sheet variant ONLY — other overlays get their own
> motion configs later (same shape, separate instances).
> Locked: full travel, slide not fade, default ON, presets
> smooth/snappy/custom, reduced-motion forces instant.

## What

- `lib/search/motion.ts`: shared shape + preset table (smooth 240
  ease-out matches collapse rhythm; snappy reuses wave curve).
- Settings: `search.sheetAnimation` admin/resolved/builtins; resolver
  maps preset → concrete (generic merge would pass names through raw —
  caught by tsc, fixed via exclusion pattern).
- Component: `motion` + `closing` props → inline vars + data hooks;
  default mirrors builtins for standalone use.
- CSS: `sf-sheet-in` translate-only keyframes + `[data-closing]` exit,
  var-driven timing, reduced-motion guard. Bare `translateY(-100%)`
  tripped the wave-park guard → reworked to blessed `calc(-100% - 8px)`
  form (same subpixel physics).
- Callers: two-phase close in demo (closing → unmount 240ms; instant
  when off/reduced-motion).

## Decisions (+ rejected)

- Per-variant instances over shared motion (sheet slides, modals may
  fade — settings must not leak across variants).
- Guard conformance over guard edits (calc form, pioneer test untouched).
- Signature fix (`Required<Admin>` → concrete triple) over call-site casts.

## Verification

`tsc` clean; suite 154/154 (motion 3, knob e2e 1, closing 1, style 2
new); `next build` green. 12 per-file commits, local, unpushed.

## Follow_ups

- V1 palette modal (reuses motion shape with its own instance + travel).
- Navbar assembler mount for production wiring.
