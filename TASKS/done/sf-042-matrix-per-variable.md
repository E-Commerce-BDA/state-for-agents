# sf-042 — Matrix per-variable tables, batch 1 (done 2026-10-13)

Rewrite grouped rows as one-row-per-variable tables (Variable |
Description | Values | Default | Paints via). Batch 1: Pill, Toast,
Badge. Step-0 grep verified all names against code before writing.

## Commits
1. Tracking. 2. Matrix batch 1. 3+. Close.

## Verification

Step-0 grep: all 10 `--pill-*` vars match globals.css; Toast props
match component; Badge props + custom fields match component +
themeSettings. `git diff --stat`: 1 file, +47/−4. Storefront and suite
untouched (docs-only). Doc commit c7e214d.

## Follow_ups
- Batch 2: Icon, Textarea, Button. Then overlays, navbar, product card.
