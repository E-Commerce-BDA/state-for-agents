# sf-007 — (auth) routes + stateful islands (done 2026-09-30)

> Reconstructed from session record 2026-10-05 (backfill).

## What

`app/(auth)/{signin,signup,forgot}/page.tsx` (server: fetch → resolve →
vars → props; `?next=` internal-path guard; `?token=` post-link step;
chromeless — no header/footer until finalized) + `_components/` islands
(SigninForm/SignupForm/ForgotForm: validation display, eye toggle,
meter, loading, marked `TODO(auth-client)` stubs). Per-page form titles
added to settings (tables rule over code). Forgot dead-code branch
(request-step ok message unreachable) caught by tests, restructured.

## Decisions (+ rejected)

- Server pages + client islands over client pages: CMS read + cookies stay
  server-side; state stays in islands. Rejected all-client pages (secrets
  would leak to browser).
- Stubs marked `TODO(auth-client)` surface documented envelope copy —
  honest preview, no fake success paths.

## Verification

7 island tests (jsdom submit + 3s async waits documented); `tsc` clean;
`next build` green with `/signin /signup /forgot` routes. Suite 111/111
with slice. Commits C0–C9 pushed to `main`.
