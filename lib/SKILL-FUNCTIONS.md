# SKILL-FUNCTIONS — good vs bad functions

> Scope: all TS. Small, pure, typed, single-purpose. Resolvers own `??`; components don't.
> Status: Active | Date: 2026-09-30

## Rules

1. One job per function, name says it (`resolveButtonBg`, not `getData`); explicit param + return types; no hidden I/O in "pure" helpers.
2. `??` / defaults live **only** in resolvers (`lib/cms/*`, service layer) — components and queries receive final values.
3. Validate at entry (Zod/DTO), fail fast with coded errors (`{code, message, requestId}`); never swallow errors or return `null` silently.
4. Keep functions short enough to test in one case table; prefer early returns over nesting.

## Good vs bad

```ts
// GOOD — pure, typed, single job, default owned here
export function resolveRadius(override: number | undefined, global: number): number {
  return override ?? global;
}
// BAD — vague, untyped, fetches + renders + defaults inside a component
export async function getStuff(props: any) {
  const d = await fetch('/api/x').then(r => r.json());   // I/O in render helper
  return <div style={{ borderRadius: props.r ?? 8 ?? null }}>{d.x}</div>;
}
```

Use next: SKILL-INTERFACES (types), SKILL-DUMB (where functions may live).
