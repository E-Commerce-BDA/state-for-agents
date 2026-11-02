# sf-063 — blog routes + legal pages from CMS content (done, 2026-11-02)

## What

The footer's About/Privacy/Terms links and the home's journal teaser had no
destination pages. This task built them: `/blog` + `/blog/[slug]` from cms-svc
blogs, and `/about`, `/privacy`, `/terms` from cms-svc pages — all copy lives
in Mongo and is editable through the CMS, so "nothing is UI-only" holds for the
shell pages too. Ships in the same storefront commit as `sf-060`/`sf-062`
(`e879214`); the tags and revalidation behind it are `cms-008`.

## How

- `app/(shop)/blog/page.tsx` — published list, ISR 300 + `cms:blogs` tag.
- `app/(shop)/blog/[slug]/page.tsx` — `generateMetadata` +
  `generateStaticParams`, block renderer (`components/blog/PostBlocks.tsx`) for
  heading/paragraph/image/quote; plain `<img loading="lazy">`, no pipeline.
- `lib/blog/present.ts` — blog list/detail presentation helpers (dates,
  excerpts), pure and unit-tested.
- `app/(shop)/about|privacy|terms/page.tsx` — share
  `components/pages/PageBlocks.tsx` (rich_text/image/cta/faq from
  `GET /cms/pages/:slug`, tag `cms:pages:{slug}`); a missing or inactive page
  is `notFound()`, never a stub.
- `lib/pages/richText.ts` — dependency-free allowlist sanitizer for admin
  rich_text HTML: `p/h2-h4/ul/ol/li/strong/em/br` and internal `a` only;
  everything else is stripped.
- Prose/FAQ styles in `app/globals.css` on the shell gutter; text measure via
  `max-width` on the prose element (the `sf-060` layout rule).
- `proxy.ts` untouched — every new route is public static.

## Decisions (+ one rejected alternative each)

1. **Content from cms-svc pages/blogs, not static TSX** — editable-through-CMS
   is only true if the copy lives in Mongo; rejected: hardcoded legal pages
   with a "later migrate" note, which is how the old footer happened.
2. **Hand-rolled allowlist sanitizer instead of `dangerouslySetInnerHTML` or a
   library** — the admin is trusted, the browser is not; an allowlist of nine
   tags is small enough to audit and unit-test, and adds no dependency to the
   storefront's runtime. Rejected: DOMPurify (a second trust root for content
   the schema already constrains).
3. **`notFound()` for missing/inactive pages** rather than a fallback copy — a
   rendered placeholder for a page the admin deactivated is worse than a 404.
4. **Plain `<img loading="lazy">` in blog bodies** instead of `next/image` —
   the block bodies are admin-authored HTML; rewriting them into optimized
   markup is the media-pipeline task, not this one.

## Verification

| Check | Result |
|---|---|
| storefront suite (`pnpm test` at `e879214`) | 137 files / 1160 tests green, incl. `test/app/(shop)/blog.test.tsx`, `test/lib/blog/present.test.ts`, `test/lib/pages/richText.test.ts` (script/attribute stripping, internal-links-only) and the legal-route tests |
| live | `/blog` lists the 3 seeded posts; `/blog/[slug]` renders blocks; `/about` renders banner + FAQ from the page document; `/privacy` ≈40 KB of real policy prose; all 200 |
| commit | `frontend/storefront` `e879214`; docs rows in `Documentation` `b584a72` (`pages/routing.md` legal/blog routes) |

## Open

- Blog comments / related-posts rails are not in scope; the teaser section and
  the list are the whole discovery path today.
