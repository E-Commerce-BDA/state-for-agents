# sf-083 — standalone storefront mobile filters, marquee and draggable rails

- Repo: `E:\E-Commerce` (root, standalone `storefront.html`)
- Phase: P0 · priority: P1 · kind: feature
- Started: 2026-11-27 · Finished: 2026-11-27
- Verified: 2026-11-27 in a browser at 1536×900 and 375×812

## What

`storefront.html` was enhanced in append-only CSS/JS:

- `/products` gained a mobile-only **Filters** button that opens the existing
  filter rail as a left drawer with scrim, close button, Escape handling and
  focus return. Desktop keeps the original 260px sticky sidebar. Size and
  "In stock only" filter groups are hidden; category, price, sale and sort
  remain. Active-filter count appears on the button.
- The homepage brand strip is now a configurable infinite CSS marquee driven
  by `THEME_CONFIG.brandStrip` (`motion`, `speed` 20–200 px/s clamped,
  `direction`, `pauseOnHover`, `cellWidth`, `gap`, `items`). It uses a
  duplicated track, `translateX(-50%)`, `--marquee-duration`, and a static
  reduced-motion face. Labels are customizable per item.
- Horizontal sections use one reusable rail engine: pointer/touch drag with
  click suppression, `scroll-snap`, cloned edge cards for infinite wrap,
  prev/next buttons and pagination dots. Applied to New this week, category
  showcase, testimonials and the compare table drag surface.
- All paint uses existing design tokens (`--border`, `--color-accent`,
  `--surface-hover`, `--scrim`, `--z-*`, radii, typography).

## Verification

- 23/23 preserve blocks remain byte-identical after every pass.
- Extracted inline JS passes `node --check`.
- Browser at 375×812: filter button `display:flex`, size/stock groups
  `display:none`, open sets `aria-expanded=true`, focuses close, scrim open;
  close returns focus; marquee computed `animationName=sf-marquee`,
  `--marquee-duration=21.20s`, 2 track groups; rails show 4 dots and 2 clones.
- Rail scroll container expanded from 328px to 1540px; synthetic touch drag
  moved `scrollLeft` 0→200; four Next clicks wrapped index back to 0 with
  `scrollLeft=520`.
- Browser at 1536×900: filter button hidden, sidebar still sticky; marquee
  runs. Reduced-motion emulation: `animationName=none` and one cloned group
  hidden. `window.__errors` null on all tested routes.

## Caveats

- The compare table is drag-enabled but has no infinite-loop pagination,
  because a comparison table has no meaningful repeated pages.
- Brand strip cells are wordmarks; logo images are not wired in this standalone
  prototype.
- `storefront.before-mobile.html` is a backup of the pre-change file;
  `storefront.original.html` and `storefront.rebuild.html` remain from sf-082.

## Follow-ups

- Remove the backups once the user is satisfied.
- If ported to the Next app, add the mandated contract/resolver/style trios.


## Post-close alignment fix (2026-11-27)

The mobile filter button was moved into the sort-controls flex row so it sits on
the same line as the Sort by label and select, with matching 37.6px height on a
375px viewport. Its icon was changed from sliders-horizontal to Lucide's
funnel-shaped ilter. The drawer transition was removed after the browser
harness left the transition stuck at its start frame, which kept the panel
off-screen; open/close is now immediate and reliable. All 23 preserve hashes
still pass and 
ode --check is clean.
