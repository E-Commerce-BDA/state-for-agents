# sf-027 — Palette fit (done 2026-10-11)

Modal overflows the viewport (screenshot). Shrink to 720px + tighten
stack + backstop + sticky footer. Pure CSS + style-test; zero markup.

## Reference values used (E:/E-Commerce/index.html, values only)
- Card 640px → we take 720 (rows need width); root scrolls; rows cap 380.
- Not copied: radius, colors, hover fills, transitions (theme-only rule).

## Commits
1. CSS shrink. 2. Style-test extend. 3+. Gate + close.

## Verification

`tsc` clean; suite 212/212 (fit assertions green, zero contract churn —
pure CSS change); `next build` green. Card capped 720 + viewport
backstop, footer sticky. 2 code commits, local, unpushed.

## Follow_ups

- Visual side-by-side vs reference at §17 refresh (human eye check).
- Stray `storefront_search_overlay_lab (3).html` in storefront root is the
  user's file — left untracked, never committed by agents.
