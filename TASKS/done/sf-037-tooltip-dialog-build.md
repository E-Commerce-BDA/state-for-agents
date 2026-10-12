# sf-037 — Tooltip + Dialog theme build (done 2026-10-11)

Builds the sf-036 PLANNED rows: theme.tooltip/dialog groups + Dialog
paint props. Tooltip needs zero component change (feeds style object).

## Order (one commit per file)
1. Tracking. 2. Theme groups + resolver. 3. Dialog props + CSS.
4. Tests. 5. Matrix flip + admin. 6. Gate + close.

## Verification

`tsc` clean; suite 260/260 (6 new); `next build` green. Tooltip zero
component change (style-object feed); Dialog default byte-identical
(existing suites re-prove). Matrix limits corrected to source truth
(border 0–2, font 11–14, weight 500). ~5 code commits + 2 doc commits.

## Follow_ups

- Assembler passes theme.tooltip/styleOverrides + theme.dialog props.
- Remaining matrix fills: IconButton, Card.
