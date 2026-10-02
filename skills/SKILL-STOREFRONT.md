# SKILL-STOREFRONT — composed components from base

> Scope: `storefront-ui/src/ui/` — base (`baseComponents/`) composed into product/section/cart/shell.
> Status: Active | Date: 2026-09-30 | Parent: `design-system/storefront.md §11`, `components/README.md`

## Rules

1. Base (`Button/Input/Checkbox/Radio/Toggle/Badge/Select…`) knows nothing of products — only tokens + props. Composed (`ProductCard/Gallery/VariantSelector/HeroSection/BannerSection/MiniCartDrawer/Navbar/Footer`) composes base with CMS-resolved props.
2. CMS arrays (`slides[]`, `ctas[0..3]`) render by map with stable `id` keys; `0` items = render nothing (no empty row); `>3` never reaches render (rejected at save).
3. Images: `alt` required, first-slide `eager` (LCP) rest `lazy`, `aspect-ratio` prevents CLS; variant images swap on selection.
4. Follow the per-component rule doc in `Documentation/components/` (Button doc is the template); grouped docs repeat the 5-section shape per component.

Use next: SKILL-DUMB, SKILL-CSS, SKILL-SEO.
