# SKILL-FRONTEND — route work (Server fetch + resolve → dumb props)

> Scope: Next 16 App Router in `storefront-ui` / `admin-app`. Smart at shell, dumb below.
> Status: Active | Date: 2026-09-30 | Parent: `pages/routing.md`, `5.Features.md`

## Rules

1. Route folder owns `page.tsx + loading.tsx + error.tsx`; Server Component fetches (`lib/api-client/*`, Redis first) + resolves P>S>G (`lib/cms/resolve.ts`) → passes final props down.
2. Smart state (Zustand cart/compare, React Query, form drafts) lives only in route islands (`'use client'`), never in `ui/`.
3. Query rules per `pages/routing.md`: path = identity, query = ephemeral view state (filters/sort/`ids`/cursor/`preview`/`next`/variant keys); never qty, form contents, tokens, PII in query.
4. Canonical + JSON-LD per page (see SKILL-SEO); `?preview=1` reads drafts, never pollutes Redis.

Use next: SKILL-STOREFRONT or SKILL-ADMIN, SKILL-SEO, SKILL-DUMB.
