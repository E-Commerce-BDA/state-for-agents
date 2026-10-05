# sf-010 — NavLinks File 1 (done 2026-10-05)

> Reconstructed from session record 2026-10-05 (backfill). Learner-owned
> with guided review (Learning Mode loop).

## What

`lib/shell/navSettings.ts` corrected (`current: boolean` added to
`ResolvedNavLink` — spec gap the learner caught); `components/shell/
NavLinks.tsx` (props → accessible markup: `aria-current="page"`,
`data-highlight`, conditional badge); flat `.sf-navlinks` selectors on
anchors with `--nb-*` vars; badge pill hook + paint; 5 contract tests
incl. hook-binding guard. Typo-class defects (`--nv-hover`,
`.sf-navlnks`, `&` nesting) caught in review, fixed before commit.

## Decisions (+ rejected)

- `key={href}` (stable across renders) over `categoryId` (empty on custom
  links → duplicate keys). Taught via reconciliation mechanics, not rule.
- Flat selectors over nesting; `var(--color-sale)` token over invented
  sale vars. Rejected unresolvable vars (dead knobs).

## Verification

`tsc` clean; 5/5 green; diff pure-addition. Commit `b64a66d`, on `main`
(unpushed with slice — push on learner word with File 2+).
