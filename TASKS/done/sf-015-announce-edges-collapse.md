# sf-015 — Announce edge arrows + dismiss + collapse animation (in-progress, started 2026-10-10)

> Owner: agent. Locked: arrows pinned to left/right edges, close already
> optional via `dismissible` (verified, no work), collapse ON by default
> with reduced-motion forcing instant.

## What

- Settings: `collapseAnimation?: boolean` → required resolved → builtin
  `true` (motion that can be refused is a knob).
- CSS: arrows/dismiss absolute via top/bottom + auto margins (translateY
  trips the wave-park guard — reworked, guard intact); grid-rows collapse
  wrapper; reduced-motion kills transition (duplicate auth rule removed,
  existing block kept).
- Island: two-phase dismiss (closing class → unmount 220ms; instant when
  off/reduced-motion; `matchMedia` typeof-guarded for jsdom).
- Resolver passthrough needed no new logic (generic merge carries it).

## Decisions (+ rejected)

- Absolute-via-inset over transforms (guard owns translate syntax).
- Instant dismiss paths over uniform delay (never make users wait out a
  transition).

## Verification

`tsc` clean; suite 134/134 (resolver +2, bar +1, island async rework).
Commits `d76c4b6,58d04e2,c10d1da,08be590,8ec80d7,79c568b,e27d8ba,
437fa7b` (per-file), local, unpushed.

## Follow_ups

- Timer/rotation hook (File 8 era); countdown live strings.
