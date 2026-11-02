# ec-006 — contracts 1.12.0: section extensions + footer schema (done, 2026-11-02)

## What

`sf-060` needed four things the 1.11.0 section schemas could not express: a
viewport-height hero, CSS-marquee settings on the brand strip and testimonials,
a manual-vs-newest source on featured products, and an optional admin-entered
name beside each brand logo. `sf-062` needed a footer document that no existing
module owned. This is a backward-compatible minor release — field extensions on
types that already exist, plus one new schema file — not new section types.

## How

- `src/schemas/section-settings.ts` — `heroSettingsSchema` += `height:
  "auto"|"viewport"`; `brandStripSettingsSchema` += `motion: "static"|"marquee"`,
  `speed` (int 20..200), `direction`, `pauseOnHover`; `testimonialSettingsSchema`
  += `layout: "grid"|"marquee"`, `speed`, `pauseOnHover`; `SECTION_SETTING_KEYS`
  extended with the six new keys.
- `src/schemas/section-content.ts` — `featuredProductsContentSchema` +=
  `source: "manual"|"newest"`; `brandStripContentSchema` += ordered
  `items: [{brandId: uuid, label? ≤60 chars}]` (`brandIds` stays for
  logos-only payloads); `testimonialItemSchema` += `rating 1..5`, `verified`,
  `date`.
- `src/schemas/section-catalog.ts` — `SECTION_CATALOG.allowedSettings` rows
  updated per type so the CMS accepts exactly what the schemas accept.
- `src/schemas/footer.ts` (new) — `footerSchema` `.strict()`: `columns ≤6`
  (title + `{label, href}` links), `social {label, url}`, `legal`, `contact
  {email?, phone?, address?}`, `logo?: imageRef`, `wordmark?`, `tagline?`,
  `copyright?`, `paymentIcons ≤8`; `footerResponseSchema {footer, version}`.
  Exported from `index.ts`.
- `package.json` 1.11.0 → **1.12.0**, CHANGELOG, `pnpm pack`; the tarball is
  committed and repinned in **cms-svc and storefront** only (catalog-svc and
  search-svc read no section/footer schema; their pins are unchanged).

## Decisions (+ one rejected alternative each)

1. **Extend existing types** rather than add `marquee`/`reviews`/`collection`
   types — the types already own content and ordering, and a new type costs a
   catalog row, a CMS branch and a renderer forever. Rejected: one
   `branded_marquee` type that duplicates two behaviors into one name.
2. **Per-item `label`** instead of a section-level `showNames` toggle — the
   requirement is "optional name beside **each** logo", which only a per-item
   field can express; the label also needs no catalog fetch to render.
3. **No newsletter block in `footerSchema`** — there is no endpoint to submit
   to, so the schema would encode a promise the platform cannot keep.
4. **`items` alongside `legacy brandIds`** rather than replacing it — payloads
   written before this release keep parsing; the renderer prefers `items` when
   present. Rejected: a breaking rename, which a minor bump cannot carry.

## Verification

| Check | Result |
|---|---|
| `pnpm test` | **148 tests in 7 files** green (`footer.spec.ts` 11 new; `section.spec.ts` 26 incl. new-fields-accepted, unknown-keys-rejected, 1.11.0-payloads-still-valid cases) |
| typecheck / build / pack | green; `ecom-contracts-1.12.0.tgz` contents inspected (`dist/schemas/footer.*` present) |
| repin consumption | cms-svc `6a0bd69` and storefront `e879214` build and pass their suites against the new tarball |
| commit | `ecom-contracts` `a9eaacb` (9 files, +566/−9), local-only |

## Open

- 2.0.0 (`ec-004`) still owns the dual-read retirement; 1.12.0 is another
  additive rung on the same ladder.
