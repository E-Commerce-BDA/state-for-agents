# sf-032 — Badge customs + Icon color + Textarea paint (done 2026-10-11)

Admin customization for Badge (custom creator), Icon (house defaults +
stroke color), Textarea (paint props + theme). Unlike sf-031, small
additive component changes required (tone map + missing paint props).

## Locked answers (user)
- Badge: custom creator (border type + border/bg/text colors).
- Icon: size/stroke/filled/color house defaults.

## Order (one commit per file)
1. Tracking. 2. Badge tones prop + test. 3. Textarea props + test.
4. Icon color + test. 5. Theme groups + resolver. 6. Resolver tests.
7. Matrix + admin touch. 8. Gate + close.

## Verification

`tsc` clean (caught bad SVG cast mid-flight, fixed); suite 235/235
(9 new); `next build` green. Builtins byte-identical (existing suites
re-prove). ~9 code commits + 2 doc commits, local, unpushed.

## Follow_ups

- Assembler passes theme + custom tone map into components (wiring).
- Remaining matrix fills: IconButton, Dialog, Card.
