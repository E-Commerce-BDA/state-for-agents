# sf-045 — Matrix batch 4: navbar (done 2026-10-13)

Rewrite Navbar section per-variable (Variable | Description | Values |
Default | Paints via). Group-level state tags replace the State column.
Step-0: knob paths + unions + limits verified in navSettings.ts; paint
hooks verified in globals.css (--nb-*) and live component props;
bar/logo/regions have no consumer yet (marked wiring-pending, never
invented).

## Commits
1. Tracking. 2. Section rewrite. 3+. Close.

## Verification

Step-0: knob paths + unions + limits in navSettings.ts; `--nb-*` hooks
in globals.css; live props in NavLinks/AnnouncementBar; unwired groups
(bar/logo/regions/account/cart/mobile) confirmed consumer-free.
`git diff --stat`: 1 file, +101/−10. Storefront + suite untouched.
Doc commit 566e764.

## Follow_ups
- Batch 5: product card (PLANNED until P3).
