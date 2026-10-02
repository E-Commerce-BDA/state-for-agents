# SKILL-CSS — clean CSS (tokens only)

> Scope: all UI. Tokens flow server → inline style → bare var. No hex in components.
> Status: Active | Date: 2026-09-30 | Parent: `design-system/storefront.md §3`, `components/button.md §4`

## Rules

1. Never write a hex literal in `components/` — use `var(--color-*)` / `var(--border)` / `var(--text-muted)`; values arrive via inline `style` from resolver.
2. One shared geometry per component (variants differ by vars only); parked layers rest at `100% + ≥8px` (never bare `%` — subpixel bleed).
3. Dead elements (disabled/loading) get no hover/transition by default; hover selectors carry `:not([disabled]):not([aria-disabled="true"])`; disabled face = explicit solids, never `opacity`.
4. Focus-visible ring is fixed (`2px accent + offset 2`), not customizable. Respect `prefers-reduced-motion` (wave off).

## Good vs bad

```css
/* GOOD */ .sf-btn { background: var(--btn-bg); border: var(--btn-bw) solid var(--btn-border); }
/* BAD  */ .sf-btn-primary { background: #0077B6; } /* hex in component = fails review */
```

Use next: SKILL-DUMB, SKILL-STOREFRONT.
