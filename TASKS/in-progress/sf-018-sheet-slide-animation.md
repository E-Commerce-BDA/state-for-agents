# sf-018 — Sheet slide animation, per-variant motion (in-progress)

> Owner: agent. Scope: sheet variant ONLY — other overlays get their own
> motion configs later (same shape, separate instances).
> Locked: full travel (-100%), slide not fade, default ON, presets
> smooth/snappy/custom, reduced-motion forces instant.

## What (planned)

- `lib/search/motion.ts`: shared `OverlayMotionField` type + preset
  table (`smooth 240 ease-out`, `snappy 180 wave-curve`) — reusable shape
  for future variants, per-variant instances.
- Settings: `search.sheetAnimation` (admin) → required resolved →
  builtins (enabled, 240, ease-out). Preset resolves to concrete
  ms+easing in the resolver; components never switch on preset names.
- Resolver: clamp duration 150–500, easing allowlist (unknown → ease-out,
  never inject raw strings into CSS).
- Component: `motion` + `closing` props → inline vars + `data-closing`.
- CSS: `sf-sheet-in` keyframes (translateY only, zero opacity), exit via
  `[data-closing]` transition, reduced-motion guard.
- Callers: two-phase close (closing → unmount after duration; 0ms when
  off/reduced-motion).
- Tests: preset mapping, allowlist rejection, closing render, CSS asserts
  (keyframes, no opacity, guard), island timing.

## Open

- None yet.
