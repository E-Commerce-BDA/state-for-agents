# sf-020 — Inspect query input row (in-progress, started 2026-10-10)

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

## Open

- None yet.
