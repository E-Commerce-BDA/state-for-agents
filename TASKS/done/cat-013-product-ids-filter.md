# cat-013 — `ids` filter on the product list (done, 2026-11-02)

## What

The CMS "Most Popular" section is manually curated (`featured_products`,
`source:"manual"`). Manual curation needs one thing catalog-svc did not have: a
way to fetch an exact set of products in an exact order. Without it the
storefront would have to filter a paged list client-side, which silently drops
picks that are not on the fetched page — the difference between a curated rail
and a fake one.

## How

- `src/products/dto/product-query.dto.ts` — `ids` on the list query:
  comma-separated UUIDs, validated per element (`IsUUID`), max 24, rejected
  with 400 on any malformed value.
- `src/products/products.repository.ts` — when `ids` is present the list query
  appends `id = ANY($n::uuid[])` alongside the existing `status='active'`
  guard and orders by `ARRAY_POSITION(ids, id)` so the response follows the
  input order, not the table's.
- Tests: `products.service.spec.ts` unit cases + new
  `test/product-ids.e2e-spec.ts` (170 lines): input order preserved, the
  24-cap, bad-UUID → 400, and drafts/archived rows never leaking through an
  `ids` hit.

## Decisions (+ one rejected alternative each)

1. **Server-side filter with `ARRAY_POSITION` ordering** rather than
   client-side filtering of paged results — paged filtering is honest only
   when the whole set fits one page, and a curated rail is exactly the case
   where it does not. Rejected: `limit=100` + client pick, the shape the
   storefront's old demo home used.
2. **Cap at 24** — one section's `maxItems` can never exceed a card grid; an
   uncapped `ANY()` turns a curated rail into an unbounded query.
3. **`status='active'` still applies** — `ids` selects *which* active products,
   it does not unlock hidden ones; a manual pick of a draft must render as
   absent, not leak. Rejected: an admin-style bypass on a public route.

## Verification

| Check | Result |
|---|---|
| `pnpm test` | **160 unit in 24 files** green |
| `pnpm test:e2e` | **127 passed, 5 skipped (13 files passed, 2 skipped suites)** green — re-run 2026-11-02 after the seed-fixture guard (`sf-064`) restored the two fixtures the shared dev DB needed |
| live | `GET /catalog/products?ids=<3 uuids>` round-trip preserved input order; bad UUID → 400 |
| commit | `catalog-svc` `b1db46b` (4 files, +216/−1), local-only |

## Open

- The contracts pin stays at 1.9.0 — the DTO is local validation and the wave
  shipped no catalog response schema, so no repin was needed (plan §10.10).
