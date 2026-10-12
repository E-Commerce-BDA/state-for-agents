# sf-041 — product.md hover deltas (done 2026-10-11)

Docs-only: `hoverMode: none`, swap-animation set (a) reading locked,
hover-state card/CTA paint vars, trio twins stated. 3 surgical edits,
5 insertions / 3 deletions, diff-stat verified before commit.

## Locked answers (user)
- Swap animation = (a) hover image-swap transition style (fade/slide/
  zoom/none + duration); (b) content-change animation deferred to the
  listing slice (card never knows siblings).

## Verification
`git diff --stat`: 1 file, +5/−3. Storefront untouched.
Doc commit 53646d4.

## Follow_ups
- P2 ProductCard.tsx + trio (umbrella sf-039).
- (b) listing enter/exit transitions (listing slice).
