# sf-082 — recreate the Next storefront UI in the standalone HTML prototype

- Repo: `E:\E-Commerce` (root, standalone `storefront.html`)
- Phase: P0 · priority: P1 · kind: feature
- Started: 2026-11-27 · Finished: 2026-11-27
- Verified: 2026-11-27 against the live Next app and the rebuilt HTML

## What

Rebuilt `storefront.html` to match the current Next storefront screens while
keeping the HTML's preferred designs intact. The work was done in an append-only
copy (`storefront.rebuild.html`) and, after approval, copied over the original.
The pre-rebuild file is backed up as `storefront.original.html`.

Rebuilt pages: home, cart, checkout and confirmation, account/orders/order
detail, wishlist, compare (new hash route + table + tray), search results page,
blog list/detail, auth signin/signup/forgot, and about/privacy/terms. Cart
drawer, mobile drawer, quick view and toasts were also moved to the Next visual
language. A second `:root`/`@theme inline` bridge adds the Next-only tokens
without touching the original token block. All changes are appended after the
preserved ranges; variable render functions are redefined later in the same
script scope and preserved routes delegate back to the originals.

## Preserved byte-for-byte

23 hashed blocks from `storefront-preserve-hashes.json`, all verified PASS after
the replacement: tokens; button wave system; slider; announcement CSS; navbar
CSS; megamenu CSS + data; search overlay CSS + renderers; toast CSS; product
card CSS; footer CSS + renderer; image fallback; CATEGORIES/PRODUCTS/COUPONS;
state and machines; Actions; shared renderers; navbar/megamenu renderers;
products listing and PDP renderers.

## Verification

- Next baseline screenshots captured at 1536×900 and 375×812 for 16 routes.
- Rebuilt HTML served on :8899 and screenshotted for every variable route.
- Independent browser measurements at 1536×900: home H1 `48px / 52.8px`,
  x=50, y=394.9 (Next) vs y=395.7 (rebuild); cart empty title `20px`, y=328.8
  vs y=329.6 — within 1px.
- `storefront.html` SHA-256 before replacement unchanged throughout the work;
  replacement verified byte-identical to the tested rebuild; backup verified
  byte-identical to the original.
- `window.__errors` empty on every tested route; focus-visible ring, reduced
  motion and image fallback verified.

## Caveats

- Preserved chrome intentionally differs from Next: SHORE wordmark vs Next.7,
  the HTML nav/megamenu/footer and original announcement copy remain as-is.
- Media images for hero/blog/auth/about reference the Next app's
  `/media/seed/...` paths, so exact photos require the Next app to be running.
- Residual spacing: mobile hero text ~10–20px lower, about title ~17px higher,
  blog card titles 17px vs apparent ~20px in the baseline.
- The Next `/search?q=boot` baseline was a 404; the rebuild implements the
  intended results page rather than reproducing that 404.

## Follow-ups

- Tune the three residual spacing differences if desired.
- Remove `storefront.original.html` and `storefront.rebuild.html` only after
  the user is satisfied with the replacement.
