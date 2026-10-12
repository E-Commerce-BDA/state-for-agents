# sf-040 — product.md amend (done 2026-10-11)

Note: umbrella sf-039 (product card P1–P4) stays in-progress for the
remaining P2–P4 phases; this entry records the finished doc-phase
delta only (renamed from sf-039 to avoid an id clash).

Docs-only per user order (product.md ONLY — zero component/code work).
A full product.md already existed (prior pass, implementation-detailed);
this turn adds the locked deltas only.

## Delta (one line, §9 theme sketch)
Tablet cap-3 legibility rationale (~220px floor) + `cardWidth /
cardHeight` caps. All other locked decisions (touch toggle, compare
page|modal, hoverMode, single-attribute reservation) were already in
the doc — verified, not duplicated.

## Mishap + repair (read this)
First attempt overwrote the whole file with a slimmer rewrite (commit
7661553, +115/−46 — pure loss). Caught via diff stat before closing.
Repaired with `git revert --no-commit HEAD` + recommitted as one-line
amend (6821926). Net vs pre-work: exactly 1 line. Lesson: read the
existing file FIRST on docs turns ("amend" means diff-then-touch, and
`git diff --stat` is the proof before any close).

## Verification
`git diff HEAD~2 HEAD --stat`: 1 file, 1 insertion, 1 deletion.
Storefront untouched. Both index rows already referenced product.md
(README row 26, §14 line 386) — no index change needed.

## Follow_ups
- P2 ProductCard.tsx + trio (on your word).
- P3 theme.productCard group + matrix rows.
- P4 showcase grid demo.
