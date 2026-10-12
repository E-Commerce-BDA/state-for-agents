# sf-038 — Button theme wiring (done 2026-10-11)

Theme object prop on Button (trio-lowest precedence) + AuthForm first
production wiring + showcase themed row. Demos stay explicit.

## Order (one commit per file)
1. Tracking. 2. Button theme prop. 3. AuthForm + showcase row.
4. Precedence tests. 5. Matrix. 6. Gate + close.

## Verification

`tsc` clean; suite 264/264 (4 new precedence); `next build` green.
No-theme renders identical (existing suites re-prove). 3 code commits
+ 1 doc commit, local, unpushed.

## Follow_ups

- Remaining primitives wire one per turn (Input next).
- Assembler passes resolved theme (production pipeline).
