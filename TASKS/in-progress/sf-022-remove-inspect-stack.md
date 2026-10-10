# sf-022 — Remove inspect stack, restore V2-only (in-progress, started 2026-10-10)

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

## Open

- None yet.
