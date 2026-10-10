# sf-021 — Inspect list+preview+actions regions (in-progress, started 2026-10-10)

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

## Open

- None yet.
