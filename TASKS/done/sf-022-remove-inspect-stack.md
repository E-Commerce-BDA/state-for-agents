# sf-022 — Remove inspect stack, restore V2-only (done 2026-10-10)

> Owner: agent. The built inspect modal doesn't match the reference photo
> (bare strip vs full rows/preview/actions). Forward deletion, not revert:
> work is interleaved with keeper commits across shared files, so ~20
> individual reverts would conflict everywhere. History stays as the record.

## What (planned)

- Demo wiring (§16) → region components + hook + pdp files + their tests
  → shell + spotlight + their tests → CSS blocks → knob/resolved/builtins
  → resolver wiring → registry line + union member. Consumers first,
  providers last. Gate after every layer (suite green while code
  disappears).
- Keep: motion families + `travel`, SKILL-MOTION (+commit), sheet/classic/
  demo, keeper tests, all history (sf-019/020/021 logs stay done).

## Verification

`tsc` clean; suite 156/156 (22 inspect tests removed with their code,
keeper tests untouched); `next build` green with `/components`
(§14 sheet + revised §15, no §16). Zero-code-ref grep clean
(`SearchInspect|Spotlight|demoPdp|useInspectPreview|sf-inspect`).
13 removal commits (9 code + 4 tracking pattern amended below),
local, unpushed. Compiler-as-finder caught every straggler
(resolveNav test asserts); wave-park guard never touched.

## Follow_ups

- V1 palette modal (own motion instance); navbar assembler mount.
- History (sf-019/020/021 logs + commits) preserved as the record.
