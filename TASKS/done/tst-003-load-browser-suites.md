# tst-003 — k6 and Playwright suites

- Repo: `ecom-infra` (suites); storefront fix in `frontend/storefront`
- Phase: P5 · priority: P2 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `2fd216e` (first specs), `bc94539` (axe/SEO), `9354f2a` (edge + live runs), `4a2eba4` (storefront a11y/SEO fixes)
- Verified: **2026-11-26 against the live stack and a real Nginx edge**

## What

Four k6 load scripts and four Playwright browser flows are implemented, plus
`a11y-seo.spec.js` covering axe WCAG A/AA, accessible names, keyboard focus,
reduced motion, title/canonical/OG/JSON-LD/sitemap/robots and a screenshot
baseline. `tests/README.md` carries an explicit coverage ledger: spec claim →
suite file → actual status. `Documentation/9.Testing.md §6/§7` was amended to
match that ledger rather than claiming coverage the suites do not provide.

## Verification (live)

- k6 **v2.4.0** was installed into a temp directory (no system-wide change);
  `pdp-400-variants` **PASS** (p99 36ms) and `suggest-burst` **PASS**
  (p99 8.8ms), both with 100% checks.
- `cart-mutation` passed 2,309/2,309 checks but p99 was **1.6s vs the 100ms
  target**; `checkout-ratelimit` saw **zero 429s** because no rate limiter is
  implemented in order-svc or the edge. These are product gaps, recorded as
  follow-ups rather than hidden by relaxing the thresholds.
- Public `nginx:stable-alpine` was pulled and run with `nginx/nginx.conf` on
  the compose network; edge routing for the storefront and seven service
  prefixes was confirmed (also closes `inf-004`).
- `BASE_URL=http://127.0.0.1:8080 pnpm test:e2e`: **5 passed / 5 failed / 0
  skipped**. Standalone `pnpm test:a11y-seo` after the storefront fix:
  **5 passed / 1 failed** — the remaining failure is a pre-existing
  search-focus assertion (the sheet focuses its input on open, so Tab moves to
  Cancel).
- Storefront fixes in `4a2eba4`: Sale nav contrast 2.81:1 → 5.76:1 via a dark
  text token, real `app/sitemap.ts` + `app/robots.ts`, OG and JSON-LD metadata.
  Gates: lint 0 errors / 40 advisory, typecheck clean, 1,393 tests, webpack
  build green.
- Gates: infra `pnpm test:local` 59/59; all four `check:*` scripts green;
  `node --check` clean.

## Caveats

- Lighthouse itself remains unrun (binary absent); only its DOM/HTTP facts are
  asserted.
- The screenshot baseline was intentionally deleted and recreated after the
  color change. There is no approved reference baseline, so screenshot
  comparison is not yet a gate.
- Four original browser flows still fail for fixture/UI reasons, and the two
  k6 product gaps above remain open as follow-ups.

## Follow-ups

- Implement an order-svc or edge checkout rate limiter so `checkout-ratelimit`
  can see 429s.
- Investigate the 200-line cart p99 latency gap (target <100ms).
- Fix the pre-existing search-focus assertion or the sheet behavior.
- Supply an approved screenshot baseline and a Lighthouse binary for the
  remaining spec claims.
