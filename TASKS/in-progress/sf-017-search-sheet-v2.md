# sf-017 — Search sheet V2 (in-progress, started 2026-10-10)

> Owner: agent. Easiest-first order; one version only this turn.
> Locked: trap behavior (feel-test), props-only, lazy preview fetch,
> demo quick-actions, global search only, Oceanic theme mapping.

## What (planned)

- Settings knob `search.overlayVariant` + `searchPlaceholder`
  (generic merge carries values, no resolver logic).
- `lib/search/source.ts` (SearchSource port + result type) +
  `demoSource.ts` (throwaway-by-replacement).
- `app/hooks/useSearch.ts` (query, 300ms debounce, min-2 gate,
  AbortController stale-kill, source-injected).
- `components/shell/SearchSheet.tsx` + barrel (dumb: sheet, pills,
  cards, arrow-cycle callbacks; no fetch).
- `.sf-searchsheet` CSS (Oceanic mapped); contract + style tests.
- `searchRegistry.ts` (dynamic import per variant; build proves
  unselected absent).
- Showcase §14 + variants index (all 5 named, statuses marked).

## Open

- None yet.
