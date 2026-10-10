# sf-016 — Search overlay demo, trap vs light (done 2026-10-10)

> Owner: agent. Props-only locked regardless of winner; trap-vs-light
> decided by feel in this demo, loser deleted.

## What

- `/components` showcase §13: mode toggle (trap / light) + open button.
- Demo overlay in-page (TEMPORARY, delete-at-launch): big bar, popular
  row, demo product grid passed as props from a local stub filter marked
  `TODO(hook-era)`.
- Trap variant: Tab cycles inside (recomputed per keypress for dynamic
  lists), Esc closes, focus returns to trigger. Light: autofocus + Esc
  only. Query state corrected mid-build to live in the parent (props-only
  violation caught before commit).

## Decisions (+ rejected)

- Demo inside the showcase file over a production component: nothing
  demo-grade enters `components/`. Rejected early production build (winner
  unknown).
- `aria-modal` true only under trap (honest semantics per mode).

## Verification

`tsc` clean; 134/134 unchanged (demo intentionally untested — temporary);
`next build` green with `/components`. Commit `63034ae`, local, unpushed.

## Follow_ups

- Winner pick after feel-test; production `SearchOverlay.tsx` follows
  (contract + style trio); loser deleted with its section.
