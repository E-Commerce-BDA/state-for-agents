# sf-067 — PDP CMS sections: per-product description, details, reviews, related, trust, story, FAQ (done, 2026-11-08)

## What

The PDP is no longer hardcoded. Each product has a materialized CMS section set at `pdp-${product.id}` with seven admin-controlled types: `pdp_description`, `pdp_details`, `pdp_reviews`, `pdp_related`, `pdp_trust`, `pdp_story`, and `pdp_faq`. The storefront reads exactly that page key; `pdp-default` is a blueprint cloned per product and is never read at runtime. The buy box no longer contains hardcoded trust badges, description, details, or related products.

## How

- `@ecom/contracts` `1.14.0`: seven PDP section types, catalog `group`, tolerant `sectionListEnvelopeSchema`, and `cloneSectionsSchema`.
- `cms-svc`: `POST /cms/admin/sections/clone` copies a page key in one Mongo transaction, one revision bump, one outbox event, and one target cache tag. The Mongoose enum is now derived from `SECTION_TYPES`.
- Storefront: `getSections` validates the envelope and parses per-section, so one unknown section cannot blank the page. The resolver gains a product context and PDP builders. `pdp_related` reuses `ProductCollectionViewModel` and `ProductCollectionSection`. `pdp_reviews` reuses `TestimonialSection` with `id="reviews"` on the first active reviews section. Outage fallback builds only description/details/trust/related from catalog/static data; an empty successful CMS response renders no sections.
- Seed/backfill: `ecom-infra/scripts/demo-seed/content.mjs` now defines the seven-section `pdp-default` template. `seed-demo.mjs` clones it per product through admin APIs, preserves existing product sections by default, and supports `SEED_RESET_PDP=1` for replace. `scripts/backfill-pdp-sections.mjs` is dry-run by default.

## Decisions (+ one rejected alternative each)

1. **Materialized blueprint over runtime template inheritance** — the editor can distinguish “no sections” from “inherits the template,” and a blueprint edit cannot silently rewrite every product. Rejected: runtime template + per-product override state, which cannot represent those two cases cleanly.
2. **One clone endpoint over a bulk clone endpoint** — transactions stay bounded and auditable; backfill loops one target at a time. Rejected: a bulk `{toPageKeys[]}` endpoint whose failure semantics would need partial-success reporting.
3. **Outage-only built-in fallback** — a successful empty response is explicit absence. Rejected: falling back whenever a product has no sections, which would make admin edits indistinguishable from a missing materialization.
4. **Authored-only ratings** — the summary averages numeric ratings on CMS-authored review items only. Rejected: treating unrated quotes as zero-star reviews, which would invent a rating the admin never wrote.

## Verification

| Check | Result |
|---|---|
| `@ecom/contracts` | `pnpm run typecheck` and `pnpm test` green (158 tests) |
| `cms-svc` | `pnpm run typecheck` and section service spec green (14 tests) |
| Storefront typecheck | `npx tsc --noEmit` green |
| Storefront tests | `pnpm test` green (149 files, 1237 tests) |
| Storefront webpack build | `npx next build --webpack` green |
| Seed scripts | `node --check` clean for `content.mjs`, `seed-demo.mjs`, and `backfill-pdp-sections.mjs` |

Live seed verification was not run because the local CMS/Mongo stack was unavailable in this session.

## Follow-ups

- `adm-001`: add the admin “Apply default” action and a new-product clone hook; until then use `pnpm --dir ecom-infra pdp:backfill`.
- Decide whether to delete the legacy slug-keyed demo PDP rows; they are unreachable but still stored.
- Do not mark demo review quotes as `verified` unless they are verified.
