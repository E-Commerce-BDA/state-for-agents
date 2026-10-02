# SKILL-DUMB — dumb contract + smart-shell/dumb-leaves

> Scope: every `ui/` + `components/` file. The core readability rule of this project.
> Status: Active | Date: 2026-10-02 | Parent: storefront `AGENTS.md` §3 (single home; component docs defer to it)

## Rules

1. **Dumb contract:** `props → JSX` only. No fetch, no store, no CMS import, no `??` defaults, no hex — bare `var(--x)` in CSS, values via inline `style`.
2. **Smart shell / dumb leaves:** the route shell (or section composer) is the last smart layer — it fetches, resolves P>S>G, handles state. Every level deeper is dumber; leaves only render.
3. Escape hatches on everything: `className` merged (never replaced), `style` merged after internal, `...rest` + `forwardRef` for `aria-*`/`data-testid`.
4. States via `data-*` hooks (`data-disabled`, `data-checked`); a11y attributes always set (labels, `aria-busy`, `aria-checked=mixed` for indeterminate).
5. If you need a default, a fetch, or a store subscription — you are in the wrong file; lift it to the shell/resolver.

```tsx
// GOOD (leaf) — final values in, JSX out
export function Badge({ tone, children, style }: { tone: Tone; children: ReactNode; style?: CSSProperties }) {
  return <span className="sf-badge" data-tone={tone} style={style}>{children}</span>;
}
// BAD — smart leaf: fetches, defaults, imports store
export function Badge({ tone }: { tone?: Tone }) {
  const t = tone ?? useStore(s => s.tone); useEffect(() => { fetch('/api/tone'); }, []); ...
}
```

Use next: SKILL-CSS, SKILL-INTERFACES, SKILL-FUNCTIONS.
