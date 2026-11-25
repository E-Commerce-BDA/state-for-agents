# sf-071 — restore lint with an ESLint flat config (done, 2026-11-25)

- Repos: `frontend/storefront` (+ `Documentation`)
- Phase: P5 | priority: P1 | kind: chore | transport: docs
- Started: 2026-11-25 | Finished: 2026-11-25

## What

`pnpm lint` was dead because Next 16 removed `next lint`. Replaced it with an
ESLint 9 flat config using `eslint-config-next` 16's `core-web-vitals` and
typescript-eslint. Dead code is a hard error; the four new React Compiler rules
are advisory warnings. Removed the 29 unused imports, state setters, a
parameter and a dead proxy helper the first run reported.

## Why

The repo already declares ESLint/typescript-eslint in 2.Tech-Stack.md, so a
flat config restores the intended tool without a second toolchain. A lint gate
that cannot fail is not a gate, hence the hard unused-vars rule; refactoring
the established dumb components to satisfy new React Compiler rules is a
separate change and stays advisory. Removing dead code beats prefixing it with
underscores just to silence the gate.

## How

- `eslint.config.mjs` — flat config, generated-path ignores, hard/advisory split.
- `package.json` — `lint: eslint .`, eslint + eslint-config-next + typescript-eslint.
- 29 dead identifiers removed across 11 files, no behavior changes.
- `9.Testing.md` — lint listed as a live gate.
- Commits: `95dcb75` (storefront), `e4dcca1` (Documentation).

## Verification

| Check | Result |
|---|---|
| `pnpm lint` | exit 0, 0 errors, 40 advisory warnings |
| probe file with an unused import | fails with `@typescript-eslint/no-unused-vars`, then removed |
| `npx tsc --noEmit` | green |
| `pnpm test` | 161 files / 1290 tests |
| `next build --webpack` | green, all pages generated |

## Follow-ups

The 40 React Compiler warnings are advisory; addressing them is a separate
component refactor.
