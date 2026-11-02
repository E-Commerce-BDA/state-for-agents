# sf-060 — CMS-driven home and full-bleed section set (done, 2026-11-02)

## What

The storefront home was the `sf-051` teaser: a hardcoded `DEFAULT_HERO` plus the
eight newest products. This wave made the whole page render from cms-svc — seven
ordered sections (hero, newest, categories, brand marquee, reviews, manual
"Most Popular", blog teaser), each editable through the CMS admin API with no
storefront redeploy — and replaced the 1280px page container with the
full-bleed shell the design docs now codify. It consumes contracts 1.12.0
(`ec-006`), the catalog `ids` filter (`cat-013`) and the cms-svc
footer/revalidation parity (`cms-008`); the footer/blog/legal shell is
`sf-062`/`sf-063` and the data behind it is `sf-064`.

## How

- `app/globals.css` — `--sf-page-pad: min(50px, 4vw)`; `.sf-shop` loses
  `max-width:1280px` and becomes the fluid shell on the same gutter as the
  navbar/footer containers. Text measure (hero copy, legal prose) constrains the
  **text element**, never the page — decision recorded in the docs first.
- `lib/cms/tags.ts` — `cms:sections:{pageKey}`, `cms:footer`, `cms:blogs`,
  `cms:pages:{slug}` added to the allowlist; authored together with cms-svc's
  `storefrontTags` so the two vocabularies cannot drift (parity test in cms).
- `lib/cms/client.ts` — `getSections/getFooter/listBlogs/getBlog/getPage`,
  never-throw/null envelope, now validated with the 1.12.0 schemas (closes the
  file's own "swap in contracts schemas after repin" note).
- `lib/catalog/client.ts` — `listBrands()` + `ids` pass-through.
- `lib/sections/{viewModels,resolveSections}.ts` — fan-out resolver: inactive or
  empty sections are skipped; a dead service skips only its own section (empty ≠
  outage); per-section settings flow into the product-card knobs (A2.6).
  `blogTeaserModel` treats empty `postIds` as "latest published, capped by
  count" because cms blog ids are Mongo ObjectIds and the contracts field is
  `uuid[]` — documented in the file, not hidden.
- `components/sections/` — block per type + `SectionRenderer` registry; hero >1
  slide → `HeroCarousel` client island; brand strip and testimonial marquee are
  pure CSS (duplicated track, pause on hover/focus, `prefers-reduced-motion`
  renders static); each brand cell = logo `<img>` + optional admin-entered
  `label` beside it, wordmark fallback when the logo is missing.
- `app/(shop)/page.tsx` — fetches sections with
  `next: { tags:['cms:sections:homepage'], revalidate: 300 }`, resolves, renders
  `<SectionRenderer>`; `DEFAULT_HERO`/demo `FeaturedGrid` path deleted.
- Docs, committed before the CSS (`Documentation` `1033405` design-system +
  routing rule change, `bf02632` section blocks, `b584a72` footer/blog/legal):
  `design-system/storefront.md` §4/§8, `pages/routing.md` §2, `pages/home.md`,
  `pages/components/sections.md`.

## Decisions (+ one rejected alternative each)

1. **Extend the existing section types** (1.12.0 minor) instead of new
   marquee/reviews/collection types — the types already own content and
   ordering; new types would triple the contracts+CMS+renderer surface.
2. **`ids` filter server-side in catalog-svc** for manual "Most Popular"
   (`cat-013`) instead of client-side filtering of a paged list — paged
   filtering is a lie, the SQL path is index-friendly and permanent.
3. **CSS marquee** instead of a JS carousel — server-rendered, a11y-cheap,
   reduced-motion native; no client island needed.
4. **Per-item `label` on brand-strip items** instead of a global show-names
   toggle — the admin chooses per logo which name appears, and the text needs
   no catalog fetch.
5. **Full-bleed page, component-level text measure** — the rule is about the
   page container; an edge-to-edge legal page is unreadable, so max-width lives
   on the text element. Rejected: keeping a 1280px page container "for safety".
6. **`DEFAULT_HERO` deleted rather than kept as fallback** — a fallback that
   renders when CMS data exists is fake content; outage degradation is the
   client's null envelope + section skip, proven live.

## Verification

| Check | Result |
|---|---|
| storefront `pnpm test` | 137 files / 1160 tests green at `e879214` |
| storefront `tsc --noEmit` / `next build --webpack` | exit 0 / clean |
| commit | `frontend/storefront` `e879214` (95 files, +7077/−343, branch `staging`, one cohesive commit with `sf-062`/`sf-063` + seed media); docs `1033405`/`bf02632`/`b584a72` |
| live data plane | `GET /cms/sections?pageKey=homepage` → 7 sections, sortOrder 0..6 in the shipped order; `?ids=` round-trip preserves input order; bad UUID → 400 |
| live render | `GET /` renders all sections from DB (8/8 content markers, ≈166 KB); hero copy, marquee, manual picks, journal teaser all DB-sourced |
| live admin loop | `PATCH /cms/admin/sections/hero-homepage` sentinel headline → storefront reflects after one `POST /api/revalidate`, no redeploy; revert verified; `/api/revalidate` without the secret → 401 |
| live degradation | cms-svc stopped → `GET /` answers 200 with no error boundary (stale-while-error from the Data Cache in dev); the minimal-fallback render path is covered by the `sf-062` FooterMount tests |

## Open

- `/api/track` (`sf-052`) and the catalog cache-invalidation hook (`sf-061`)
  remain open; neither blocks the home.
- Section images are committed assets under `public/media/seed/` (`sf-064`);
  the pipeline through cms media/S3 uploads is out of this wave's scope.
