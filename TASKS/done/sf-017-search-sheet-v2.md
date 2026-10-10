# sf-017 — Search sheet V2 (done 2026-10-10)

> Owner: agent. Easiest-first order; one version only this turn.
> Locked: trap behavior (feel-test), props-only, lazy preview fetch,
> demo quick-actions, global search only, Oceanic theme mapping.

## What

- Settings knob `search.overlayVariant` + `placeholder` (generic merge
  carried both, zero resolver logic).
- `lib/search/source.ts` (port + abort contract) + `demoSource.ts`
  (throwaway-by-replacement, abortable delay).
- `app/hooks/useSearch.ts` (seq-guarded stale-kill on top of abort).
- `components/shell/SearchSheet.tsx` (dumb; trap added after feel-test
  verdict) + honest registry (unbuilt → null, never wrong variant).
- `.sf-searchsheet` CSS (Oceanic mapped; style-contract caught 3
  literals, fixed through navbar vars).
- Contract (6) + hook (4) + style (3) tests; showcase §14 live + §15
  variants index (all 5 named with statuses).

## Decisions (+ rejected)

- Trap in production component (feel-test verdict), not demo-only.
- Registry honesty over scaffolding (null fallback beats wrong render).
- Query state corrected to parent mid-build (props-only violation
  caught before commit).

## Verification

`tsc` clean; suite 147/147 (13 new); `next build` green with
`/components`. 14 per-file commits, local, unpushed.

## Follow_ups

- V1 palette modal next (reuses hook + source untouched).
- Navbar assembler mount for production wiring.
