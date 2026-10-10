# sf-019 — Inspect modal shell + motion families (done 2026-10-10)

> Owner: agent. Phase 1 of V4 inspect modal: shell div only, then motion
> families. Regions (list/preview/actions) land next turns. Locked:
> oceanic modal-adapted travel (scale+rise, NOT sheet -100%),
> per-variant instances, additive presets, trap behavior, Oceanic theme.

## What (planned)

- Motion families in `lib/search/motion.ts` (oceanic/fast/flat additive;
  smooth/snappy byte-identical) + tests.
- `SKILL-MOTION.md` (families, preset discipline, reduced-motion law).
- `search.inspectAnimation` knob + resolved + builtins (oceanic).
- `components/shell/SearchInspect.tsx` shell (backdrop + frame + close,
  empty slots, trap, motion/closing props) + `SpotlightButton.tsx`.
- `.sf-inspect` + `.sf-spotlight` CSS; shell tests; showcase demo.
- Tracking close + per-file commits + unpushed upkeep, local only.

## Verification

`tsc` clean; suite 165/165 (motion 5, knob e2e 1, shell 4+4 new);
`next build` green with `/components` §16. Per-file commits, local,
unpushed. Oceanic scale+rise chosen over sheet travel (distance-velocity
rule); backdrop fade is chrome dimming, not content motion.

## Follow_ups

- List region (pills, rows, inspect affordance) → preview (lazy PDP,
  sizes, stock) → actions (demo Add-to-bag, Full Page) → registry line.
- SKILL-MOTION.md + router lane (this turn).
