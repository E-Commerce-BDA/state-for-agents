# sf-044 — Matrix batch 3: overlays (done 2026-10-13)

Rewrite Sheet/Editorial/Palette subsections per-variable (Variable |
Description | Values | Default | Paints via). Why-differ table +
shared paragraph untouched. Step-0: CSS vars harvested from globals.css,
knob paths verified in navSettings.ts before writing.

## Commits
1. Tracking. 2. Section rewrite. 3+. Close.

## Verification

Step-0: `--searchsheet-*`/`--nb-*`, all `--ed-*`, all `--pl-*`
harvested from globals.css; knob paths verified in navSettings.ts
(incl. eyebrowColor). `git diff --stat`: 1 file, +73/−31.
Rationale blocks untouched. Storefront + suite untouched.
Doc commit 27db040.

## Follow_ups
- Batch 4: navbar. Batch 5: product card (PLANNED until P3).
