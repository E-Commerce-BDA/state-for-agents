# sf-023 — Editorial search takeover (done 2026-10-11)

Photo-exact full-screen scrollable overlay (user Image 1). Palette deferred to sf-024.

## Locked answers (user)
- Trending purple badge → new lilac token trio + `BadgeTone "lilac"`.
- Overlay default bg → existing `--color-section-bg` (new token only on 2nd consumer).

## Build order (one commit per file)
1. Settings: `NavSearchField.editorial?: EditorialField` + resolved + builtins + limits
   (bg/bgAlpha 0-100/blur/blurPx, eyebrow+archive+title texts+colors, input/placeholder/
   underline, closeIcon, tab colors + tabShape v1-only `pill`, cardType v1-only
   `standard`, cardRadius 0-24, dept/name/price colors, editorialAnimation oceanic).
2. `resolveNav` editorial instance (nested merge + motion exclusion + clamps).
3. Lilac tokens + Badge tone; `tagTone()` lib map; demoSource CATALOG export.
4. `SearchEditorial.tsx` (trap+Esc+return, arrows+Enter, curated prop, theme object).
5. `.sf-editorial` CSS block (+ reduced-motion guard line).
6. Test trio. 7. Registry line. 8. Showcase §17 (own useSearch) + §15 flip.
9. Gate + close.

## Verification

`tsc` clean at every layer; suite 175/175 (19 new: 8 contract + 4 resolver +
7 style); `next build --webpack` green with `/components` (§16 live,
§15 flipped). CSS ships (`sf-editorial` in bundle CSS); palette absent
repo-wide in `.next` JS. Zero-straggler: tagTone/DEMO_CATALOG/lilac all
referenced. One test fixed mid-flight (bogus-easing inherits oceanic
builtin — test wrong, code right). 13 code commits, local, unpushed.

## Follow_ups

- sf-024 palette modal (own motion instance, trending+recent, quick-add).
- CMS collections replace DEMO_CATALOG; cardType/tabShape unions extend.
- `alt=""` on card imgs is deliberate (button already announces name+price).
