# SKILL-SEO — canonical, JSON-LD, performance

> Scope: storefront indexability without URL sprawl. Single authority: `pages/routing.md §5`.
> Status: Active | Date: 2026-09-30

## Rules

1. Canonical = bare slug (default = first in-stock variant); variant/filter URLs emit `rel=canonical` to it; internal links + sitemap use canonicals only.
2. `Product` JSON-LD with per-variant `offers` on the canonical page; Article JSON-LD on blogs; unique meta/OG per PDP/post.
3. LCP: first hero image `eager` + dimensions, rest `lazy`; `aspect-ratio` everywhere (no CLS); ISR revalidate on `cms.updated`.
4. Never index drafts, filtered listings, or variant URLs (defer long-tail indexing until Search Console demands it).

Use next: SKILL-FRONTEND, SKILL-STOREFRONT.
