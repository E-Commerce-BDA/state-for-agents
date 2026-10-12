# sf-031 — Theme form-controls (done 2026-10-11)

Global theme vocabulary for Button/Input/Checkbox/Toggle (admin portal
customization). Zero component changes — theme supplies defaults, flat
props keep winning.

## Locked answers (user)
- One task, four groups. House defaults included (variant + size).

## Order (one commit per file)
1. Tracking. 2. lib/cms/themeSettings.ts. 3. Resolver (same file? separate
   resolveTheme.ts — decided at build: same file, pure sibling like
   buttonAnimation.ts holds its resolver). 4. Tests. 5. Matrix + admin doc.
6. Gate + close.

## Verification

`tsc` clean; suite 226/226 (4 new); `next build` green. Zero component
files touched (pure lib slice). Matrix self-test: Toggle width/height
+ knob colors answerable from rows. 2 code commits + 2 doc commits.

## Follow_ups

- Assembler/production mount passes resolved theme into components
  (components read theme defaults, flat props win — wiring, not new API).
- Next matrix fills: Input doc? (no doc file yet — rows live in matrix),
  IconButton, Dialog, Card.
