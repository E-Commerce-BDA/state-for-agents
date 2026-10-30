# sf-039 — Product card (done 2026-10-30)

P1 product.md doc → P2 ProductCard + trio → P3 theme group → P4 showcase grid → gate → close.

## Completed Capabilities
- **Anatomy**: `<article>` root with accessible dual button openers for image and title (never nested).
- **Ratios**: `1:1 / 3:4 / 4:5 / 4:3 / 16:9` via `--pc-ratio`.
- **Card Types**: `standard / minimal / compact / overlay / horizontal` via `data-card-type`.
- **Independent Radii**: `borderRadius` (`--pc-radius`) and `imageBorderRadius` (`--pc-media-radius`), clamped 0–24px.
- **Image Blend Modes**: `normal / multiply / darken / overlay / screen` via `--pc-image-blend` (`mix-blend-mode: multiply` seamlessly blends white packshot cutouts).
- **Image Fit**: `cover / contain` via `--pc-image-fit`.
- **Badges**: Tag tone mapping (`tagTone`), custom tones, `badgePosition` (`left / right`), and section-level `showBadge` visibility gate.
- **Paint & Backgrounds**: `cardBg`, `borderColor`, `hoverCardBg`, `hoverBorderColor`, `cardPad`, and `textAlign`.
- **Hover Modes**: `none / image / actions / zoom` (respecting `prefers-reduced-motion`).
- **Showcase**: Added Section 19 to `app/components/page.tsx` featuring an interactive customization playground and side-by-side comparison of all 5 card types.

## Verification
- Contract tests (`test/components/product-card.test.tsx`): 9/9 passed.
- Model & resolver unit tests (`test/lib/productCard.test.ts` & `test/lib/themeSettings.test.ts`): 20/20 passed.
- Style contract tests (`test/components/product-card-style.test.ts`): 5/5 passed.
- Next.js production build: clean compile.
