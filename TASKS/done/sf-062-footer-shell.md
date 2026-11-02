# sf-062 — CMS footer shell + FooterMount (done, 2026-11-02)

## What

The storefront footer was the `sf-029` zero-state shell: hardcoded blocks with
no service behind them. The wave's footer is a cms-svc document — columns,
social, legal links, contact, logo/wordmark/tagline, copyright and payment
icons — rendered in the global shell on every page and editable through the
admin API. It ships with `sf-060` (one storefront commit `e879214`) and depends
on the cms-svc footer module (`cms-008`) and the contracts `footerSchema`
(`ec-006`).

## How

- `app/globals.css` — footer shell styles on the same `--sf-page-pad` gutter as
  the page shell and the navbar (§5 of the plan; full-bleed, no max-width).
- `lib/cms/footer.ts` — server read of `GET /api/cms/footer` through the
  never-throw envelope, validated by the 1.12.0 `footerSchema`, tagged
  `cms:footer` with `revalidate: 300`.
- `components/shell/Footer.tsx` — dumb block: columns/social/legal/contact/
  copyright/payment icons from props only, no fetch.
- `app/_components/FooterMount.tsx` — client island mounted in `app/layout.tsx`
  directly after `NavbarMount`, receiving the server-resolved footer props and
  self-suppressing on `AUTH_PATHS` (the exact NavbarMount pattern).
- Fallback: when cms-svc is down/empty the mount renders a minimal shell with
  **real routes only** (`/products`, `/about`, `/privacy`, `/terms`) — resilience
  without invented content.

## Decisions (+ one rejected alternative each)

1. **Footer as its own cms module** (`cms-008`) rather than a theme or
   navigation field — separate concern, partial updates stay safe, and it gets
   its own tag/outbox key like settings does.
2. **Minimal real-routes fallback** instead of a canned footer copy — a fake
   fallback silently defeats "nothing is UI-only"; the fallback exists only so
   the shell never 5xxes.
3. **Mount pattern copied from `NavbarMount`** rather than a server-rendered
   `<Footer>` in the layout — the auth-path suppression and the client-side
   self-hiding are already proven there; two shapes of the same problem would
   drift.
4. **Payment icons are display-only strings** (contracts caps at 8) — no
   payment-provider truth is claimed from a CMS field; rejected: deriving icons
   from order-svc providers, which would couple the shell to checkout.

## Verification

| Check | Result |
|---|---|
| storefront suite (`pnpm test` at `e879214`) | 137 files / 1160 tests green, incl. the Footer/FooterMount trio tests (block render, fallback, AUTH_PATHS suppression) |
| live | `GET /cms/footer` → columns=4, social/legal present, paymentIcons=5; footer renders on `/` from DB; About links live in the footer Company column (verified against the seeded document, not assumed) |
| degradation | cms-svc stopped → `/` still 200, no 5xx (dev served the cached page; the fallback path itself is the unit-tested one) |
| commit | `frontend/storefront` `e879214`; docs row in `Documentation` `b584a72` (shell-cart footer section rewritten for the CMS footer) |

## Open

- No newsletter block: no endpoint exists to submit to, so the schema has no
  field and the shell has no fake form.
