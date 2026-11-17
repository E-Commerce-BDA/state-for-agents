# sf-054 — storefront listing depth (done, 2026-11-17)

## What

`/products` became a full listing: a category/brand/price/tag/discounted filter
rail, a server-side sort control, append-style load-more, and a category
breadcrumb. The first page is still server-rendered for SEO; later pages go
through a same-origin BFF.

## How

- `lib/catalog/listingPage.ts` is the one loader shared by the RSC route and the
  new `GET /api/catalog/products` BFF. It parses untrusted params, resolves
  slugs, lists one page, maps cards, and derives facets + breadcrumb.
- `app/(shop)/products/_components/ListingFilters.tsx` writes the URL through
  the router; `components/commerce/FilterRail.tsx` and `SortSelect.tsx` are dumb
  controlled painters over existing primitives. Changing any filter drops the
  cursor, since a cursor belongs to one result set.
- `app/(shop)/products/_components/ListingGridIsland.tsx` owns accumulated rows
  and the cursor. It fetches page 2+ through `lib/http/browser.ts`, keeps a
  module-local cache keyed by canonical query, dedupes by id, stops at the last
  page, and shows a `role="alert"` on failure (consistent with sf-069).
- Facets come from `cat-015`'s real-row endpoint. `lib/catalog/facets.ts` builds
  the category tree, upward path, indented select options and the breadcrumb;
  an orphan `parentId` is a root rather than an invented parent.
- `Documentation/pages/routing.md` §2 was amended docs-first: bare listings keep
  no breadcrumb; a category-filtered listing gets `Home / … / Category`.

## Decisions (+ one rejected alternative each)

1. **Shared loader for RSC + BFF** — one place for slug resolution and mapping.
   Rejected: duplicating the five rules in a route handler.
2. **URL as the only state container** — shareable, reload-safe, and the sort is
   enforced server-side. Rejected: client-only filter state and a client
   reshuffle.
3. **Fix the catalog cursor first (cat-015)** — append on the old cursor would
   duplicate products. Rejected: shipping load-more against the broken walk.

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 1259 tests / 153 files green |
| `npx next build --webpack` | green, `/api/catalog/products` registered |
| Catalog e2e (keyset walk + facets) | added, not run — DB down |
