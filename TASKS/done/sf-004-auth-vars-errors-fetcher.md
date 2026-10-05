# sf-004 — Auth cssVars emitter + error map + CMS fetcher (done 2026-09-28)

> Reconstructed from session record 2026-10-05 (backfill).

## What

- `lib/auth/cssVars.ts`: resolved settings → flat `--auth-*` map (string
  assembly only; composed `--auth-input-focus-shadow`; gradient-to-CSS for
  linear/radial/conic; behavior/content/seo travel as props, never vars).
- `lib/auth/errors.ts`: total code→copy function, 7 codes pinned, unknown
  falls back to generic; login pins generic (no-enumeration as a test).
- `lib/cms/authSettings.ts`: cache-first fetcher (timeout → stale →
  null) with injected source/cache; `createCmsSource` for the future
  cms-svc envelope; malformed bodies return null.

## Decisions (+ rejected)

- Copy lives once in `errors.ts` (pages never duplicate; thin client
  reuses later). Rejected per-page copies (drift source).
- Injected interfaces over network mocks: tests stub data, never fetch.

## Verification

3 + 3 + 6 unit tests green; `tsc` clean.
