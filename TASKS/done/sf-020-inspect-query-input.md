# sf-020 — Inspect query input row (done 2026-10-10)

> Owner: agent. Root cause of the dead-click report: the shell opened
> correctly (mount, trap, Esc all worked) but rendered backdrop + empty
> frame + X — the query input belonged to no region (shell said "frame
> only", list/preview/actions didn't claim it). Locked: input row is
> shell chrome, like close.

## What (planned)

- `SearchInspect`: controlled `query`/`onQuery`/`placeholder` props +
  autofocus; decorative glyph (spotlight stays the external trigger).
- `.sf-inspect__bar` CSS (pill row, auth-input focus language).
- Demo §16 wires `useSearch` query in (results still pending regions).
- Tests: binding, autofocus, absent-regions proof.

## Verification

`tsc` clean; suite 167/167 (input binding, autofocus, half-binding proof,
bar paint asserts); `next build` green. Click path re-verified: blue
circle → shell → typing works. 5 per-file commits, local, unpushed.

## Follow_ups

- List region (filter pills, rows, inspect affordance) → preview (lazy
  PDP, sizes, stock) → actions (demo Add-to-bag, Full Page).
