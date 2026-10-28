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

## Follow-ups

- Add theme, navigation, pages, blogs, media, page-settings, event-envelope,
  and `media.resize-image` schemas + tests.
- Cut/tag `v1.0.0` and create the GitHub Release after remote/push approval.
- Pin the exact tarball URL in `cms-svc`.
- Start `cms-svc` 2.1: Mongoose models, Zod pipe, revision service, cache
  service, event port, error codes.

## Commits

- `ecom-contracts` `4d46959` — feat(contracts): add v1 CMS section catalog.
- `Documentation` `d9b3768` — docs: settle Phase 2 contracts and CMS section
  catalog.
