# sf-011 — AnnouncementBar File 2 (in-progress, started 2026-10-05)

> Owner: learner. Guide briefed; implementation pending.

## What (planned)

`components/shell/AnnouncementBar.tsx`: dumb bar — text/CTA display,
dismiss *callback* prop, countdown *string* prop (timer lives in future
hook), empty-text renders nothing. `.sf-announce` CSS via
`--nb-announce-*` vars. Contract + style legs.

## Open

- Timing state placement (hook, File 8 era) — bar takes strings only.
- Countdown format (server truth, client tick) — decided at hook build.
