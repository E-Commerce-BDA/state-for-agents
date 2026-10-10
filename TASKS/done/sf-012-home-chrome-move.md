# sf-012 — Showcase to /components, chrome on home / (done 2026-10-05)

## What

Showcase `app/page.tsx` → `app/components/page.tsx` (`git mv`, history
kept) with delete-at-launch header. New home `app/page.tsx`: mounts
AnnouncementBar + NavLinks explicitly (per-page mount — auth stays
chromeless) via `HomeChrome` island (dismiss + active-slide state only);
server resolves demo CMS-shaped input through the real resolver
(`TODO(cms-svc)` marks the live-data swap); section index below chrome
until hero lands.

## Decisions (+ rejected)

- Per-page mount over root layout (root would chrome auth too, breaking
  the conversion lock); `(shop)` group layout later, root stays html-only.
- Demo-shaped input through the real pipeline over hardcoded props:
  pipeline proven today, content flagged scaffolding (never translate,
  never A/B).
- `as const` rejected after tsc failure (readonly vs mutable arrays) —
  explicit `NavSettings` annotation instead.

## Verification

Route test (landmarks, dismiss, slide flip); `tsc` clean; 132/132;
`next build` routes `/`, `/components`, auth trio. Commits `78e8e9b,
1337425,68ae194,1ebfae1` (per-file), local, unpushed.

## Follow_ups

- Hero slice lands in home main; `/components` deleted at launch.
