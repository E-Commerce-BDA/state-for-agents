# sf-024 — Palette search modal (in-progress, started 2026-10-11)

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

## Open
- None yet.
