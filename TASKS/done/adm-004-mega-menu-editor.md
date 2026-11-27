# adm-004 — Admin navigation screen edits CMS-backed mega-menu groups through the storefront BFF with safe hrefs, reorder/promo controls and --adm-* chrome

- Repo: `admin-app`
- Verified: 2026-11-27
- Commit(s): e37f830

## What

Admin navigation screen edits CMS-backed mega-menu groups through the storefront BFF with safe hrefs, reorder/promo controls and --adm-* chrome.

## Why

Browser is never trusted; pure model gives UX feedback and BFF repeats validation. Rejected: direct CMS calls from the island.

## Verification

Coordinator verified clean trees, author identity and gates. cms: 267 unit
and 117 live e2e; admin: 103 tests, lint/typecheck/build green.

## Follow-ups

- No live cross-repo E2E; mocked BFF and pure schema tests only.
