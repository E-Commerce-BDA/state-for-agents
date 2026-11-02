# sf-064 — demo seed: committed media + idempotent admin-API seed (done, 2026-11-02)

## What

The CMS-driven home (`sf-060`), the footer (`sf-062`) and the blog/legal routes
(`sf-063`) are only real if a demo store runs on them. This task added the
generated imagery committed under `frontend/storefront/public/media/seed/` and
the idempotent seed that fills every service's admin API behind them: 6
categories, 6 brands, 14 products, navigation, theme, footer, the 7 homepage
sections in the shipped order, 3 published posts, and the about/privacy/terms
pages with actual copy. `pnpm seed:demo` from the repo root drives it over
HTTP only.

## How

- `ecom-infra/scripts/demo-seed/seed-demo.mjs` — orchestrator: registers the
  seed admin (auth-svc seeds roles but no user) and grants `admin` on the dev
  DB via the documented psql line, logs in, then walks catalog → cms →
  storefront in find-by-slug/key create-or-patch order. Idempotent by
  construction: a second run reports `0 created, 39 patched, 15 skipped`.
- `ecom-infra/scripts/demo-seed/content.mjs` — all copy/schemas-as-input:
  section content+settings, footer document, posts, pages. The journal teaser
  deliberately sends **no** `postIds` (cms blog ids are Mongo ObjectIds, the
  contracts field is `uuid[]`; the storefront resolver treats empty as "latest
  published, capped by `count`").
- `ecom-infra/scripts/demo-seed/manifest.mjs` + `http.mjs` — the data manifest
  and the shared fetch envelope (never throws; exits non-zero with a named step
  on any failed mutation).
- `ecom-infra/package.json` — `seed:demo` script.
- Assets: 16 PNGs under `public/media/seed/` (products, category tiles, 2 hero
  slides, about banner), referenced as internal `/media/seed/…` paths — the
  contracts `imageRefSchema` explicitly permits internal paths.
- `archiveFixtures` keeps the catalog e2e's own fixtures active
  (`E2E_OWNED_SKUS`) — the e2e suite runs against the same dev database.

## Decisions (+ one rejected alternative each)

1. **Seed through admin HTTP APIs, not raw SQL** — validation, the cms outbox,
   events and revalidation all fire, so seeded state equals admin-edited state
   and the seed run itself exercises the admin-edit loop. Rejected: psql
   inserts, which would silently skip the search/event/revalidation paths the
   wave is built on.
2. **Wordmark fallbacks over generated brand logos** — the image budget went to
   products, categories, hero and the about banner; the brand strip renders the
   name beside each tile either way (`label` per item), so no artwork was
   invented for logos or dedicated blog covers. Recorded as a follow-up.
3. **Fixture products archived except the two the e2e owns** — the dev DB is
   shared, and a green catalog suite is not negotiable; the first run archived
   `fixture-tee`/`fixture-mug` and turned `products.e2e-spec.ts` red, so the
   guard (`175644b`) plus the two-row SQL restore are part of this task's
   record, found and fixed during verification rather than before it.
4. **`count: 3` without ids on the journal teaser** — see How; an id list the
   schema would reject is worse than the documented "latest" behavior.

## Verification

| Check | Result |
|---|---|
| seed runs | first full run `4 created, 35 patched, 15 skipped`; post-guard re-runs exit 0, fixtures skipped, idempotent (`0 created, 39 patched, 15 skipped`) |
| live data plane | sections 7 sorted 0..6 in shipped order; footer columns=4/paymentIcons=5; blogs=3; pages about/privacy/terms; settings version round-trip; products list images present; `?ids=` order preserved |
| live commerce (the seed's proof of a real store) | guest add-to-cart → register+login → merge → checkout `201` orderId `2ab0e0f7-…` grandTotal 2300 → idempotent replay same orderId → DB rows in `"order".orders/order_items/payments` (confirmed/paid/mock capture) → `order.created` consumed: stock 34→32, cart converted (0 items) |
| live render after seed | `/` 200 with all section markers from DB; hero admin-edit → reflect → revert inside one revalidate cycle |
| commits | `ecom-infra` `f17166e` (5 files, +1456/−1) + `175644b` (e2e-fixture guard); storefront media inside `e879214` |

## Open

- Regenerate brand logos + dedicated blog covers when image credits allow
  (follow-up recorded on the entry).
- The seed assumes gate order storefront → cms → catalog running with
  `REVALIDATE_SECRET` set on both sides; otherwise the seed still lands and the
  cache settles within one TTL (documented, not a bug).
