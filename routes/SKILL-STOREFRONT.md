# SKILL-STOREFRONT — composed components from base

> Scope: `frontend/storefront/components/` — `ui/` base composed into
> `auth/` (shipped) and later product/section/cart/shell. Applies to the
> storefront-ui repo only.
> Status: Active | Date: 2026-10-02 | Parent: `design-system/storefront.md §11`, `components/README.md`

## Rules

1. Base (`Button/Input/Checkbox/Radio/Toggle/Badge/Select…`) knows nothing of products — only tokens + props. Composed (`AuthPage/Split/Panel/Form`, later `ProductCard/Gallery/VariantSelector/HeroSection/MiniCartDrawer/Navbar/Footer`) composes base with CMS-resolved props.
2. CMS arrays (`slides[]`, `ctas[0..3]`) render by map with stable `id` keys; `0` items = render nothing (no empty row); `>3` never reaches render (rejected at save).
3. Images: `alt` required, first-slide `eager` (LCP) rest `lazy`, `aspect-ratio` prevents CLS; variant images swap on selection.
4. Stateful forms are route islands (`app/(auth)/_components/`, `app/hooks/` shared) — never inside composed blocks; islands ship with their route's tests.
5. Follow the per-component rule doc in `Documentation/components/` (Button doc is the template); grouped docs repeat the 5-section shape per component.

Use next: SKILL-DUMB, SKILL-HOOKS (stateful composition), SKILL-CSS, SKILL-SEO.
