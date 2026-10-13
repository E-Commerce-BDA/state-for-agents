# sf-043 — Matrix batch 2 + unpushed clear (done 2026-10-13)

Batch 2 per-variable tables (Icon/Textarea/Button) + clear all unpushed
arrays (user pushed everything; verified empty rev-lists on all three
repos before clearing).

## Commits
1. Tracking. 2. Clear arrays. 3. Matrix batch 2. 4+. Close.

## Verification

Step-0 grep: Icon defaults + ICON_NAMES union, Textarea props +
`--ta-focus`, Button `--btn-*` + `--wave-*` + `--pressed-*` all match
code; two draft corrections applied (wave-border, pressed names).
`git diff --stat`: 1 file, +51/−5. Storefront + suite untouched.
Doc commit faea6f6. Arrays cleared after empty rev-lists on all repos.

## Follow_ups
- Batch 3: overlays. Batch 4: navbar. Batch 5: product card.
