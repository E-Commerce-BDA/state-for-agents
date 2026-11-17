# sf-055 — PDP depth (done, 2026-11-17)

## What

The PDP gained four behaviours the feature spec already promised: variant URLs
with history, photo-settings precedence, a compare tray and `/compare`, and
CMS-controlled related-by-brand.

## How

- `app/hooks/useVariantFromURL.ts` + `lib/commerce/variantUrl.ts`: pure codec
  maps `?Color=ocean-blue&Size=m` (option names in `position` order, value
  slugs — never ids) to a value-id selection. A committed choice pushes
  history; an invalid/out-of-stock URL is repaired to the nearest purchasable
  variant with a quiet `role="status"` notice and `router.replace` — never a
  404.
- `lib/commerce/photoSettings.ts`: `product > section > global` merge with
  clamps (`gutter 0–48`, `widthPercent 25–100`, custom ratio 0.5–2.5). The
  global face is a new optional `photoSettings` layer in contracts 1.16.0 and
  `resolveThemeSettings`. `Gallery` receives paint props only.
- `app/_components/CompareProvider.tsx` + `lib/commerce/compare.ts`:
  session-only tray (no localStorage, per AGENTS.md §5) with a 4-item cap;
  `ProductCard.onCompare` is a real toggle; `/compare?ids=a,b` fetches the
  products through the existing catalog `?ids=` read.
- `pdpRelatedContentSchema.source` gained `"brand"` in contracts 1.16.0;
  `pdpRelatedModel` queries `catalog.listProducts({ brandId })` and skips when
  the product has no brand.
- Docs-first: `components/product.md`, `6.Admin-Panel.md`, `4.API-Design.md`,
  `8.Versioning.md` updated.

## Decisions (+ one rejected alternative each)

1. **Client hook over RSC redirect** — routing.md §4 forbids a 404 on a bad
   variant URL and wants Back to step through tried variants. Rejected:
   server-side validation that would blank the product page.
2. **One pure photo resolver** — precedence decided once, clamped once.
   Rejected: reading `photoSettings` in Gallery, cards and the panel.
3. **Session tray, URL artifact** — the tray is transient; the shareable
   artifact is `/compare?ids=`. Rejected: localStorage (hard-banned) and a
   cookie/BFF hop.
4. **Enum value over new section type** — admins keep one related-products
   editor. Rejected: a second `pdp_related_brands` type.

## Verification

| Check | Result |
|---|---|
| contracts `tsc`, 163 tests, build, pack (1.16.0) | green |
| storefront `tsc --noEmit` | green |
| storefront targeted tests (38) | green |
| storefront full test + `next build --webpack` | see final gate run |

## Follow-ups

- The catalog e2e for `cat-015` (keyset walk + facets) is still unrun because
  the local DB is down; migration `010` still needs applying.
- Section-level photo knobs are not yet in any PDP section settings schema —
  the section layer exists in the resolver but currently carries no values.
