# SKILL-INTERFACES — null vs required, who owns defaults

> Scope: TS types + Zod across UI and services. Rule: absent key = inherit; never store `null`.
> Status: Active | Date: 2026-09-30 | Parent: `6.Admin-Panel.md §5`, `components/button.md §2–3`

## Rules

1. A field is **required** only if the thing is invalid without it (`headline`, `image` on a slide; `text`+`link` on a present CTA). Everything customizable is **optional** (`bg?`, `radius?`) — absent means "inherit from section → global → default".
2. Never type customizable fields as `| null`. Reset/inherit = **delete the key**, never write `null` (Mongo JSONB + P>S>G rely on absence).
3. Every interface has a Zod mirror in `@ecom/contracts` (e.g. `ctasSchema = z.array(ctaSchema).max(3)`); validate at boundaries (admin save, API input, Mongoose pre-save), not in render.
4. Display names show where a value resolves from (instance/section/global/default); forms prefill resolved values but store only edited keys (sparse).
5. DB row types mirror `3.Database-Schema.md` columns exactly (no renaming); `DECIMAL` stays string.

## Good vs bad

```ts
// GOOD — optional inherits, required enforced, Zod mirrors
type Cta = { id: string; text: string; link: string; bg?: string; radius?: number };
// BAD — nullable customization leaks nulls into P>S>G; required-vs-optional unclear
type Cta = { id: string; text: string | null; link?: string; bg: string | null };
```

Use next: SKILL-FUNCTIONS (resolvers own `??`), SKILL-DUMB (components use bare vars).
