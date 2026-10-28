# cms-002 — Phase 2.0 contracts + CMS section catalog

## What

Started Phase 2 for `cms-svc` by creating the standalone `ecom-contracts`
repo and the first `@ecom/contracts@1.0.0` package slice. The slice locks the
CMS section inventory, per-type content shapes, settings allowlists, and the
admin edit matrix before any `cms-svc` domain code is written.

The package is local-only and `private: true`. It has not been pushed, tagged,
or published as a GitHub Release.

## How

- `E:/E-Commerce/ecom-contracts` — new git repo on `main`.
- `package.json` — ESM + `.d.ts`, exact-pin consumers, Zod 4 peer, TypeScript 6,
  Vitest 4, `pnpm pack` release tarball.
- `src/schemas/common.ts` — keys, UUIDs, hex colors, internal paths, image
  refs, ISO dates, CMS revision.
- `src/schemas/cta.ts` — CTA shape + `max(3)`.
- `src/schemas/section-types.ts` — canonical seven types.
- `src/schemas/section-content.ts` — per-type content schemas.
- `src/schemas/section-settings.ts` — per-type settings allowlists.
- `src/schemas/section-catalog.ts` — `SECTION_CATALOG` admin governance.
- `src/schemas/section.ts` — discriminated union, list response, reorder.
- `test/section.spec.ts` — 17 contract tests.
- `README.md`, `CHANGELOG.md`, `VERSIONING.md` — catalog, admin matrix, semver,
  release workflow.
- `.github/workflows/release.yml` — tag-gated build/test/pack/GitHub Release.
- `Documentation/services/cms.md` — settled six decisions + section catalog +
  Phase 2 build order.
- `Documentation/8.Versioning.md` — exact tarball distribution and semver rules.
- `Documentation/0.Project-Overview.md`, `Documentation/2.Tech-Stack.md` —
  aligned index, Zod 4, GitHub Release tarball.

## Locked decisions

- `@ecom/contracts@1.0.0`; standalone repo; exact GitHub Release tarball;
  ESM + `.d.ts`; Zod 4 peer.
- Sparse section overrides only; storefront resolver remains the merge
  authority; `version` is the global CMS revision.
- Section types: `hero`, `banner`, `featured_products`, `category_showcase`,
  `brand_strip`, `blog_teaser`, `testimonial`.
- Admin may create/delete/reorder/activate and edit `title`, `content`,
  `settings`, `isActive`.
- `key`, `pageKey`, and `type` are create-only/immutable; `sortOrder` is
  server-managed via reorder; timestamps/version are read-only.
- `featured_products` uses manual ordered `productIds` only in v1.
- Empty section content is valid but skipped by the storefront; `null` is
  rejected; omit keys to inherit.
- Save = publish for sections/settings/nav/theme/pages; blogs keep
  `status: draft|published`.
- Media uses one shared bucket per env, cms-svc owns `media/`, no SVG.
- Atlas staging nightly/7-day, production hourly/30-day; upgrade to M10 + PITR
  at >350 MB or RPO <1h.

## Verification

- `pnpm typecheck` — clean.
- `pnpm test` — 17/17 passing.
- `pnpm build` — clean.
- `pnpm pack` — `ecom-contracts-1.0.0.tgz`.
- Tarball smoke install in a temp consumer — import + `sectionSchema` parse +
  seven catalog entries passed.

## Progress Across Slices

- **Slice 2.0a, 2.0b, 2.0c**: Contributor identity hygiene complete, docs aligned, `@ecom/contracts@1.0.0` tagged and packed.
- **Slice 2.1 (cms-svc Foundation)**: Mongoose schemas, RevisionService (`cms_meta`), CacheService (Redis graceful degradation), EventsService (`IEventBus`), ZodValidationPipe.
- **Slice 2.2 (Sections, Settings, Navigation)**: Section CRUD, atomic reordering via bulkWrite, global theme settings, page auth settings, navbar settings, public cache-aside.
- **Slice 2.3 (Pages and Blogs Subsystem)**:
  - `cms_pages` Mongoose collection with `slug` index, `PageBlock` union (`rich_text`, `image`, `cta`, `faq`), revision bumping, and Redis caching.
  - `cms_blog_categories` and `cms_blogs` collections with compound indexes `{ status: 1, publishedAt: -1 }`.
  - Base64 cursor-based pagination (`<publishedAt>|<_id>`).
  - Draft vs published editorial lifecycle; `blog.updated` event dispatching on publish/unpublish.
  - 79 unit tests passing; 43 e2e tests passing against real MongoDB 8 and Redis.
  - Oxlint 0 warnings/0 errors; build clean.

- **Slice 2.4 (Media Subsystem)**:
  - `StoragePort` abstraction with `LocalDiskStorageAdapter` storing files under configurable local directory.
  - `cms_media` Mongoose collection with `key` format `media/{yyyy}/{mm}/{uuid}.{ext}`, size limit (10 MB), and MIME enforcement (PNG/JPEG/WebP/AVIF; rejects SVG).
  - Background task dispatch: emits `media.resize-image` job for responsive formats.
  - In-use guard on deletion: checks references across `cms_sections`, `cms_pages`, and `cms_blogs`; rejects with `409 MEDIA_IN_USE` if referenced.
  - 89 unit tests passing across 17 test suites; 53 e2e tests passing across 5 test suites.
  - Oxlint 0 warnings/0 errors; tsc clean; nest build clean.

## Follow-ups

- Slice 2.5: Storefront wiring (contracts package pin, shared type replacement, auth settings endpoint update).
- Slice 2.6: Full verification gate, Atlas backup runbook validation, final wrap-up.

## Commits

- `ecom-contracts` `4d46959`, `5e70c6a` — v1.0.0 release schemas & contracts.
- `Documentation` `d9b3768`, `b6b0e30` — documentation alignment.
- `cms-svc` `9d06920` — feat(cms): initialize cms-svc foundation.
- `cms-svc` `e1575cd` — feat(cms): implement sections, settings, and navigation.
- `cms-svc` `1cea2aa` — feat(pages): implement pages domain with blocks, caching, and revision tracking.
- `cms-svc` `b2a0996` — feat(blogs): implement blogs and categories domain with cursor pagination and event publishing.
- `cms-svc` `7becd21` — test(pages-blogs): add e2e integration tests for pages, categories, and blogs.
- `cms-svc` `0ac2690` — feat(auth): add CurrentUser param decorator.
- `cms-svc` `905203c` — feat(media): implement media domain with StoragePort, local disk adapter, in-use guard, and resize job publishing.
- `cms-svc` `daa1549` — test(media): add e2e integration tests for media upload, public serving, and in-use deletion guards.


