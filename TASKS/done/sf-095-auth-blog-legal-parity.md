# sf-095 — Auth, blog and legal pages reuse auth machine, PasswordMeter, safe ?next=, BlogCard and PageBlocks with styled boundaries

- Repo: `storefront-ui`
- Verified: 2026-11-27
- Commit(s): 4ec38c6

## What

Auth, blog and legal pages reuse auth machine, PasswordMeter, safe ?next=, BlogCard and PageBlocks with styled boundaries.

## Why

Reset-resume gap closed with existing safeNextPath; new layout would violate the one-source CMS rule. Rejected: new auth layout.

## Verification

Coordinator verified clean tree, author identity and four gates after each
commit. Final storefront suite: 242 files / 1627 tests, lint 0 errors
(40 pre-existing warnings), tsc clean, webpack build green. Agent served
storefront.html and next dev locally; auth and styled 404 were browser-captured.

## Follow-ups

- Full visual parity requires live CMS/auth; styled 404 and auth screens were browser-verified.
