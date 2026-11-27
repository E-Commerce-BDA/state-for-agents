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


## Drawer-shell fix (2026-11-27)

The inline filter panel was replaced with a real `.sf-drawer.sf-drawer--left`
mount, matching the cart and hamburger drawers: full viewport height, 320px
width at 375px, header with Filters title/Reset/icon close, and the shared
`.sf-scrim`. Reparenting is responsive: on <1024px the filter aside moves into
the drawer, on desktop it stays in its sticky sidebar; a resize listener
re-renders across the breakpoint. The mobile button is now icon-only
(Lucide `filter`, `aria-label="Filters"`) so Sort by fits on one line.
Verified: button 38px and vertically centered with the sort select, drawer
x=0/w=320/h=812 with role=dialog, filter category click changes the H1 to
Clothing, close returns focus, desktop sidebar intact, window.__errors null.
All 23 preserve hashes still pass and node --check is clean.


## Professional UI pass (2026-11-27)

The mobile sort row was reordered to `Sort by -> select -> funnel`, with the
funnel button last and all controls vertically centered. The filter drawer
header now contains only the Filters title and close icon; Reset moved to a
sticky bottom action bar as Clear all beside a primary Show N products button.
The cart drawer transition (0.24s cubic-bezier) was restored with a
requestAnimationFrame open, and a high-specificity open rule keeps the panel
on screen. A mobile-only 2/1 column switch was added with two icon buttons,
backed by pure machines (`nxMachines.filterDrawer`, `.gridMode`, `.sort`) and
reusable builders (`nxUI.iconButton`, `nxUI.filterFooter`). Default is 2
columns; desktop keeps its theme grid. All paint uses design tokens.

Browser verified at 375x812: sort order and alignment correct, grid 2 columns
(154px x2) switching to 1 (328px), drawer x=0 with 0.24s transition, header
Filters only, footer Clear all + Show 9 products, no console errors. At 1536px
the funnel and column switch are hidden and the desktop sidebar is intact.
