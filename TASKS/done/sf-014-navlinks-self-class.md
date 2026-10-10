# sf-014 — NavLinks self-class fix (in-progress, started 2026-10-10)

> Owner: agent. Screenshot review found the component never applies its
> own `sf-navlinks` block class, so all 8 CSS rules miss on the live home
> page (bare jammed links).

## What

- `NavLinks.tsx`: renders `sf-navlinks` by default, merged with `className`
  escape hatch (unpaintable markup was the screenshot bug).
- Contract test asserts the block class on `<nav>`.

## Verification

`tsc` clean; navlinks suite green (6/6 with the new assertion).
Commits `0697335,6bc7b3e` (per-file), local, unpushed.

## Follow_ups

- None. File closed.
