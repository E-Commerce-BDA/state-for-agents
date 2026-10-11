# MEMORY — compaction-survival index (rewrite me verbatim if context compacts)

Sources of truth: `tasks.json`, `TASKS/`, git log. This file is the index, not a copy.

## Repos
- Storefront `E:/E-Commerce/frontend/storefront` (repo `storefront-ui`, branch `main`,
  remote `E-Commerce-BDA/storefront-frontend.git`). Local-only commits; push only on human word.
- Memory repo `E:/E-Commerce/state-for-agents` (remote `E-Commerce-BDA/state-for-agents.git`).
  Same rule: never push unasked. `unpushed[]` in `tasks.json` is exact (hash + order checked).

## Constitution
`frontend/storefront/AGENTS.md`: smart→pure→dumb gradient; dumb-component guide (props→JSX,
controlled-only, flat-beats-object, single-home defaults, data-* for state, fixed a11y);
mandatory test trio (contract / resolver-unit / style-contract); paint→CSS/var-only +
layout→Tailwind; per-file local commits; Learning Mode always-on
(skip phrase: `"skip learning mode for this"`).

## Done (21 + sf-023 in flight)
sf-001 Tooltip → sf-022 inspect-removal. Search overlays: Classic fallback, Sheet V2 live
(§14 showcase), inspect BUILT then REMOVED per user photo-mismatch (sf-022 log is the
record; history never rewritten). Open after sf-023: sf-013 (learner SearchButton),
sf-024 palette (deferred — editorial jumped the queue per user).

## sf-023 editorial (this build)
Photo-exact full-screen scrollable takeover. Locked answers: lilac token trio added
(Trending badge), overlay default = `--color-section-bg` (new token only on 2nd consumer).
Settings = `NavSearchField.editorial?: EditorialField` group (bg/bgAlpha 0-100/blur/blurPx,
eyebrow+archive+title texts+colors, input/placeholder/underline colors, closeIcon color,
tab colors + tabShape v1-only `pill`, cardType v1-only `standard`, cardRadius 0-24,
dept/name/price colors, editorialAnimation oceanic default). Component `SearchEditorial`
+ `tagTone()` lib map + curated prop (empty query shows curated grid). Showcase §17
(own useSearch instance, never clobbers §14).

## Standing rules (never re-decide)
Trap wins · sparse settings (absent=inherit, never null) · motion per-variant instances,
preset→concrete, var timing, reduced-motion law · wave-park guard conformance-only ·
zero hex outside var() fallbacks + DEFAULT_* · `localStorage` banned (visit-memory only) ·
`index.html` never logged · commit `4257eb6` message says "53 sf", true count 54
(array is truth; message left stale, no rebase churn).
