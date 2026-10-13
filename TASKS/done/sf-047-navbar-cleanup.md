# sf-047 — Navbar cleanup: links gap + preview icons (done 2026-10-13)

Fix screenshot defects (link run-together from missing container rule)
+ mount account/wishlist/cart triggers disabled with coming-soon labels.
No behavior, no drawer, no counts.

## Order (one commit per file)
1. Tracking. 2–4. Trigger disabled props ×3. 5. Navbar mount icons.
6. CSS rules. 7–8. Tests. 9. Matrix. 10. Gate + close.

## Verification

tsc clean; suite 294/294 (3 new); `next build --webpack` green.
Links read as a row, actions as a tight group; preview icons render
disabled with coming-soon labels (no dead clicks). 5 code commits +
1 doc commit, local, unpushed. Working tree otherwise untouched
(user's commerce deletions intact).

## Follow_ups

- Functional wiring arrives with account/wishlist/cart slices (props +
  handlers already shaped; disabled flips to enabled).
- ProductCard-deletion question still open (sf-046 follow-up).
