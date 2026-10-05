# sf-005 — Composed auth blocks + paint (done 2026-09-29)

> Reconstructed from session record 2026-10-05 (backfill).

## What

`components/auth/*`: AuthPage (var scope + mode), AuthSplit (side/ratio/
mobile via `data-*`), AuthPanel (bg mode + sanitized HTML slots),
AuthForm (card + fields + banner/inline error + loading submit),
PasswordMeter (pure derivation), barrel. `.sf-auth` CSS block, var-only
paint (pattern dots via color-mix, overlay via ink token — zero literals).

## Decisions (+ rejected)

- Composed-dumb layer (new `components/<domain>/` + AGENTS amendment)
  over stuffing logic into pages or primitives. Rejected page-owned
  composition (duplicated across 3 routes).
- Sanitized HTML rendered with reason-commented `dangerouslySetInnerHTML`;
  danger resolved upstream, never handled in components.

## Verification

Contract (6) + style-contract (4) tests; suite caught a spec violation
(shared→forgot leak) and two test bugs (fallback hex-scan, missing
cleanup) — fixed in code/tests respectively, never blurred. `tsc` clean.
