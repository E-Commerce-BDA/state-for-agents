# sf-001 — Tooltip system (done 2026-09-19)

> Reconstructed from session record 2026-10-05 (backfill).

## What

Server-safe Tooltip: CSS `:hover`/`:focus-within` show, 200ms delay,
4-way placement with drift + arrow, controlled `open` override,
`role="tooltip"` + merged `aria-describedby`, bare-trigger render when
off/empty. Full style/motion knobs (bg/text/border/radius/font +
slide/fade/none, duration, offset), defaults = prior look.

## How

- `components/ui/Tooltip.tsx` (+ `index.ts` barrel) — flat props win over
  `styleOverrides`; `DEFAULT_TOOLTIP_STYLE` + `TOOLTIP_LIMITS` clamps.
- `.sf-tip` block in `app/globals.css` — everything through `--tip-*` vars.
- Demos in `app/page.tsx` §12; doc `Documentation/components/tooltip.md`.

## Decisions (+ rejected)

- Zero-JS positioning over floating-ui: no measuring lib in the tooltip
  path; rejected dependency for a CSS-solvable problem.
- Bare render when ineligible: ineligible elements cost zero DOM.

## Verification

`pnpm test` 72/72 (incl. `tooltip.test.tsx` + `tooltip-style.test.ts`
var-only-paint guard); `tsc` clean; `next build --webpack` exit 0.
Commit `85743fc`, pushed to `main`.
