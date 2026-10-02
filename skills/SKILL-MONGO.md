# SKILL-MONGO — Mongoose for CMS + analytics (kept)

> Scope: `cms_*` + `analytics_*` collections only. Postgres stays raw SQL.
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/3.Database-Schema.md §4`

## Rules

1. Mongoose models mirror `3.Database-Schema.md §4` fields; flexible `content`/`settings` objects validated by Zod from `@ecom/contracts` (e.g. `ctas[].max(3)`), not by schema strictness.
2. Indexes via idempotent `createIndex` in code (unique `key`/`slug`, `{page_key, sort_order}`, TTL `page_views` 30d / `cart_events` 60d for M0 safety).
3. `cms_settings.version` increments on every global save (cache-buster); never write `null` for inherit — delete the key.
4. Analytics writes are fire-and-forget from request path; reads aggregate from `daily_stats` + raw collections per `5.Features.md B15`.
5. No cross-service Mongo reads — cms-svc owns `cms_*`, analytics-svc owns `analytics_*`.

## Good vs bad

```ts
// GOOD — validated flexible content + version bump
sectionSchema.pre('save', function () { ctasSchema.parse(this.content.ctas ?? []); });
// BAD — trusting raw admin JSON, no validation, nulls stored
doc.content = req.body.content; // may contain ctas[10], nulls leak into P>S>G
```

Use next: SKILL-NESTJS (module shape), SKILL-INTERFACES (Zod mirrors types).
