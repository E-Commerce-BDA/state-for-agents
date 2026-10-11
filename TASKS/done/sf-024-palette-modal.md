# sf-024 — Palette search modal (done 2026-10-11)

Photo-exact centered modal (user Image 1, second design). Foundational:
Pill primitive (retrofit sheet+editorial same pass), 3 Icon glyphs,
trending + quickAdd ports, useRecentSearches + useQuickAdd hooks,
ratingCount port field.

## Build order (one commit per file)
A. Pill.tsx → .sf-pill CSS → barrel → Pill tests → pill.md + index rows.
B. Icon glyphs (flame/clock/arrow-up-right).
C. Ports: ratingCount + demo values; trending.ts + demo; quickAdd.ts + demo.
D. Hooks + tests. E. PaletteField + resolver. F. Component + CSS.
G. Trio. H. Retrofits (sheet, editorial). I. Registry + showcase §17.
J. search-overlays.md §7 amend. K. Gate + close.

## Locked answers (user)
- ratingCount added to port. addedIds prop for Added state.
- Retrofit same pass + useQuickAdd hook (agent recommendations accepted).

## Verification

`tsc` clean throughout; suite 211/211 (36 new + 3 auto-covered glyphs;
retrofit re-proved by 15 untouched sheet/editorial tests); `next build`
green with `/components` (§17 live, §15 flipped); `sf-searchpalette` +
`sf-pill` in bundle CSS. Wave-park caught `data-variant` mid-flight —
renamed `data-pill` atomically (guard bans it repo-wide). Two test-caught
bugs fixed visibly (Pill children, oceanic-easing expectation pattern).
~25 code commits + 3 doc commits, local, unpushed.

## Follow_ups

- sf-026 assembler (registry's first production caller + CI guarantees).
- PDP reuses useQuickAdd; cart-svc/search-svc swap the demo ports.
- CardType/tabShape unions extend with later card work.
