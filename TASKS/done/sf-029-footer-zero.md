# sf-029 — Footer zero-gap (done 2026-10-11)

Card padding-bottom → 0, footer margin-bottom → 0 (flush by geometry,
not by cancellation). Pure CSS + style-test.

## Commits
1. CSS. 2. Style-test. 3+. Gate + close.

## Verification

`tsc` clean; suite 222/222; `next build` green. Footer meets card edge
exactly (zero bottom geometry both sides). 2 code commits, local.

## Follow_ups

- None (hard-refresh §17 to see it).
