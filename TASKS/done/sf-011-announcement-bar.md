# sf-011 — AnnouncementBar File 2 (done 2026-10-05)

> Owner: learner (guided) + agent (resolver, bar, CSS, tests on request).

## What

`components/shell/AnnouncementBar.tsx`: dumb controlled carousel shell
(active slide via props, arrows/dismiss callbacks, empty renders null)
+ `.sf-announce` CSS (var-only paint, color-mix veil) + contract (5) +
style (2) tests. `lib/shell/resolveNav.ts`: cascade + strict-drop
time-filter + truncate + clamps (+7 unit tests, clock injected).

## Decisions (+ rejected)

- Controlled shell over internal timer state (hook era owns rotation).
- Strict-drop schedules (expired shown = pricing lie) over lenient-keep.
- Arrows only when 2..n items + flag; sole `??` is index safety.

## Verification

`tsc` clean; suite 130/130 at close (resolver 7 + bar 5 + style 2
included); `next build` green. Commits `422b24c,096cdc6,df1beaa,
f269ee1,4fb12d0,dbcf58a` (per-file series), local, unpushed.

## Follow_ups

- Timer/rotation hook (File 8 era); countdown live strings.
- Thin client + CMS source slices still queued behind shell.
