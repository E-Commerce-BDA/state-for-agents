# sf-091 — Home sections now resolve carousel content through ProductRailIsland/PaginatedRail and CMS section view models; brand marquee, categories, testimonials and journal teaser reuse existing dumb sections

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): c81b3dd

## What

Home sections now resolve carousel content through ProductRailIsland/PaginatedRail and CMS section view models; brand marquee, categories, testimonials and journal teaser reuse existing dumb sections.

## Why

The contract already resolves carousel; the renderer ignored it. Rejected N grid islands per strip and route-group depth inversion.

## Verification

Coordinator verified clean tree, author identity and four gates after each
commit. Final storefront suite: 242 files / 1627 tests, lint 0 errors
(40 pre-existing warnings), tsc clean, webpack build green. Agent served
storefront.html and next dev locally; auth and styled 404 were browser-captured.

## Follow-ups

- Full visual parity requires live CMS/catalog; structural/style tests cover it.
