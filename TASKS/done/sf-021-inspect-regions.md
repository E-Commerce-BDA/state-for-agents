# sf-021 — Inspect list+preview+actions regions (done 2026-10-10)

> Owner: agent. Closes the Image-1/Image-2 gap: shell today renders input
> only; this turn adds dept pills, result rows, lazy preview (sizes/stock),
> demo Add-to-bag + Full Page. Gradient-initial thumbs (no assets wired);
> demo sizes/stock in a separate PDP map (suggest payload stays tiny).

## What (planned)

- `lib/search/pdp.ts` port (`fetchProduct`) + `demoPdp.ts` (separate map,
  keyed by id) + `app/hooks/useInspectPreview.ts` (abort stale, skeleton
  status).
- `SearchInspectList.tsx` (pills, rows, INSPECT affordance, hint),
  `SearchInspectPreview.tsx` (badge, image, lookbook chip, dept, price,
  desc, sizes, stock), `SearchInspectActions.tsx` (demo Add-to-bag with
  dynamic label, Full Page).
- Shell `list/preview/actions` node slots (composition, shell stays
  region-ignorant); §16 wiring; two-column grid CSS.
- Trio per region; full gate; per-file commits, local only.

## Verification

`tsc` clean; suite 178/178 (hook 4, regions 7 new); `next build`
green. Click path re-verified end to end: blue circle → shell → typing
→ rows → hover/keyboard inspect → sizes → demo Add-to-bag. 13 per-file
commits, local, unpushed. Debugging lessons: source-identity refetch
loop (ref mirror), hint placement vs empty-state test, fixture/test
name disagreement (read the DOM), active-pill literal (badge-text
token, same fix as sheet).

## Follow_ups

- V1 palette modal (own motion instance); navbar assembler mount.
- Real product imagery replacing gradient-initial thumbs.
