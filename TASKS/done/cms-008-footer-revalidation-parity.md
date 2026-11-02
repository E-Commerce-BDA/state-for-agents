# cms-008 — footer module + revalidation parity (done, 2026-11-02)

## What

`cms-007` wired revalidation into the only three mutations the storefront read
at the time (theme, page settings, navigation) and explicitly recorded that
sections, pages and blogs sent nothing because no reader or tag existed. This
closes both halves: a footer module (the shell document `sf-062` reads), and
revalidation parity — sections/pages/blogs/footer now each emit their exact
storefront tag on every mutation, with a test that pins the two vocabularies
(`cms-svc storefrontTags` ↔ storefront `lib/cms/tags.ts`) against drift.
Contracts repinned 1.11.0 → 1.12.0 in the same commit (`ec-006`).

## How

- `src/footer/` — mirrors `settings/`: `footer.schema.ts` delegates shape to
  the contracts `footerSchema`; `footer.service.ts` public `GET /cms/footer`
  behind the Redis cache, admin `GET|PUT /cms/admin/footer` (JWT + admin role),
  one transactional `cms_outbox` record (key `footer`) + cache del + revalidate
  in `settings.service.ts`'s established order; `footer.controller.ts` +
  `footer.module.ts` wired into `app.module.ts`; `cache.service.ts` gains the
  footer key.
- `src/revalidate/revalidate.service.ts` — `storefrontTags` +=
  `sections(pageKey)`, `footer`, `blogs`, `pages(slug)`.
- `src/sections/sections.service.ts` — create/update/delete/reorder →
  `cms:sections:{pageKey}`; `src/blogs/blogs.service.ts` —
  publish/update/delete → `cms:blogs`; `src/pages/pages.service.ts` —
  create/update/delete → `cms:pages:{slug}`; `FooterService` → `cms:footer`.
  All best-effort after commit — a revalidation failure costs staleness, never
  the write (the `cms-007` contract).
- Tests: `footer.service.spec.ts` (130 lines), `footer.e2e-spec.ts` (169
  lines: public GET round-trip, admin PUT validated against `footerSchema`,
  outbox doc written in the transaction, cache invalidated), and the mutation
  specs in sections/blogs/pages assert the **exact tag list per mutation**
  (the `navigation.service.spec.ts` pattern); `revalidate.e2e-spec.ts` extended
  (+72 lines) so the parity with the storefront allowlist is proven end-to-end.

## Decisions (+ one rejected alternative each)

1. **Footer as its own module** rather than a field of theme or navigation —
   the footer has its own cache key, outbox key, tag and edit cadence; folding
   it in would make a footer edit revalidate the theme tag.
2. **Tags authored against the storefront allowlist in one wave** with a
   parity test — the plan's named risk was the two vocabularies drifting
   silently; the test fails in CI rather than in production staleness.
   Rejected: a shared constants package (a build dependency for two strings).
3. **Best-effort, post-commit, never fails a write** — same rule as `cms-007`,
   deliberately not re-litigated per module.

## Verification

| Check | Result |
|---|---|
| `pnpm test` | **159 unit in 23 files** green |
| `pnpm test:e2e` | **97 passed, 4 skipped (10 files passed, 2 suites skipped)** green — re-run 2026-11-02 (was 87 passed before the footer + parity suites) |
| live | `PUT /cms/admin/footer` → `GET /cms/footer` round-trip; a hero `PATCH` revalidated `cms:sections:homepage` and the storefront reflected it inside one cycle (`sf-060` admin-loop gate); seeded footer renders through the public route |
| commit | `cms-svc` `6a0bd69` (18 files, +709/−14, incl. the 1.12.0 repin), local-only |

## Open

- The dev `.env` JWT secret was aligned to auth-svc's (cms-svc verified tokens
  with its own local secret, so no auth-svc-issued token passed) — a `.env`
  fixup, gitignored, recorded here because the seed and live gates depended on
  it. Production config owns the real secret.
- `cms_outbox` still has no retention sweep (carried `cms-*` debt).
