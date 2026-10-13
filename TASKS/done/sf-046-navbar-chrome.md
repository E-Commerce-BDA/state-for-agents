# sf-046 — Navbar/chrome completion (done 2026-10-13)

Logo, search/account/wishlist triggers (cart: file stays, zero wiring —
deferred to cart slice), MobileDrawer, Navbar, NavbarMount, SearchMount
(absorbs sf-026), CI guarantees, trio tests, showcase §18, docs.
New files limited to assemblers (Navbar/NavbarMount/SearchMount) +
demoNavInput seam; no new primitives, no account menu, no cart wiring.
sf-013 reconciled at review (learner's SearchButton vs NavSearchTrigger).

## Order (one commit per file)
1. Tracking. 2–5. Triggers ×4. 6. NavLogo. 7–8. MobileDrawer + CSS.
9–10. Navbar + CSS. 11. NavbarMount. 12. SearchMount. 13. CI tests.
14. Trio tests. 15. Showcase §18. 16–17. Docs. 18. Gate + close.

## Incident (CSS commit repair, same turn)
`git add app/globals.css` swept a 211-line foreign deletion (entire
.sf-productcard block) into my paint commit — pre-existing unstaged
user work (parallel ProductCard refactor: component + lib + tests also
deleted unstaged, themeSettings touched). Repaired: soft-reset, file
restored, my 2 edits re-applied, recommitted additions-only (+126/-0
verified, af981fe abandoned for c290bf4). Guard test green. User's
files untouched; foreign hunk preserved at Temp/opencode/
globals-with-foreign.css. Lesson: `git diff --stat` BEFORE every
`git add` on tracked files — new files can't sweep, tracked files can.

## Verification

tsc clean; suite 291/291 (27 new); `next build --webpack` green.
Homepage renders layout chrome (no double mount); auth paths
self-suppress (tested); classic falls back to sheet (tested);
registry guard green (source-level CI guarantee). ~16 code commits +
2 doc commits, local, unpushed. Cart stays parked (file unmounted,
doc note).

## Follow_ups (open questions resolved or filed)

- ProductCard deletion: UNCONFIRMED — awaiting user answer (intentional
  rewrite vs accidental wipe). Until answered, keep clear of `commerce/`
  + product-card tests + themeSettings commerce edits.
- sf-013 reconciled: NavSearchTrigger ships as the production
  trigger; sf-013 closes superseded (learner work in its log).
- theme.button global feed beyond AuthForm; cms-svc swaps demo seams;
  revalidateTag("nav"); countdown tick; logo.position order rule;
  per-option disabled states (sf-033); Toast single-producer note.
