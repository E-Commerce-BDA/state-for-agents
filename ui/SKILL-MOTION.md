# SKILL-MOTION — motion families, preset discipline, reduced-motion law

> Scope: every animated surface (`components/`, `app/`). Motion is themed
> behavior, not decoration: same rules as paint.
> Status: Active | Date: 2026-10-10 | Parent: storefront `AGENTS.md` §3.8,
> `lib/search/motion.ts` (shape reference)

## Rules

1. **Families, not one-offs:** `oceanic` (slow deliberate full travel),
   `fast` (quick full travel), `flat` (minimal-travel nudge) + `custom`.
   Duration scales with travel distance (long travel + short time reads
   as a flinch). New surfaces pick a family; new families are a task.
2. **Preset discipline:** admin picks names, resolver outputs concrete
   ms + easing + travel. Components switch on resolved values (`data-*`,
   vars), never on preset strings. Preset tables are additive —
   renaming a stored preset breaks saved admin values (alias, don't rename).
3. **Var-driven timing:** durations/easings ride CSS vars inlined from
   resolved motion (`--<x>-duration`, `--<x>-easing`), with builtin
   fallbacks. No hardcoded `ms` in keyframes/transition declarations.
4. **Reduced-motion law:** every keyframe/transition ships its instant
   counterpart in the shared guard block. Motion that can't be refused is
   a bug; test asserts the guard covers the block.
5. **Travel vocabulary:** full = off-screen parks (`calc(-100% - 8px)`
   form — bare `%` trips the wave-park guard, same subpixel physics);
   minimal = nudges (8px). Opacity is a per-variant decision recorded at
   the variant, never a default smuggled in.

## Good vs bad

```css
/* GOOD */ [data-motion="on"] .sf-x { animation: sf-x-in var(--x-duration, 240ms) var(--x-easing, ease-out); }
/* BAD  */ .sf-x { animation: sf-x-in 240ms ease-out; } /* knob bypassed, untestable timing */
```

Use next: `ui/SKILL-CSS.md` (paint), `ui/SKILL-DUMB.md` (data hooks).
