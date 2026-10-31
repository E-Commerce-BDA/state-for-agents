# sf-049 — storefront: a thin auth client, no token in the browser (done, 2026-10-31)

## What

The auth pages could not sign anyone in. `SigninForm`/`SignupForm` ended in
`await new Promise((r) => setTimeout(r, 900))` followed by
`setError(displayFor("INVALID_CREDENTIALS"))`, and the two `TODO(auth-client)` markers were the
only spec. This task makes the storefront an actual client of auth-svc: four BFF handlers own the
tokens, the browser only ever holds an `HttpOnly` cookie and a `{user}` payload, and `proxy.ts`
gates `/account/*` and `/checkout/*` on that cookie.

## How

- `lib/auth/client.ts` (new, pure) — `createAuthClient({ baseUrl, fetchFn, timeoutMs })` with
  `login`, `register`, `refresh`, `logout`, `me`. Every call returns
  `{ ok: true, data } | { ok: false, code, status }`; nothing throws, and the 15 s abort becomes
  `SERVICE_UNAVAILABLE`.
- `lib/auth/errors.ts` — `SERVICE_UNAVAILABLE` added; `displayFor(code)` now covers transport
  failure separately from a rejected credential.
- `lib/auth/session.ts` (new) — the only place the cookie names and attributes live:
  `sf_at` (`Max-Age=900`, `Path=/`), `sf_rt` (`Max-Age=2592000`, `Path=/api/auth`), `HttpOnly`,
  `SameSite=Lax`, `Secure` only in production; plus `readCookie` and `clearedCookies`.
- `lib/auth/next.ts` (new) — `safeNextPath(value)` promoted from the inline `NEXT_RE` in
  `signin/page.tsx`; refuses `//evil.com`, absolute URLs and anything that is not a leading-slash
  path. Used by the page, the refresh route and the proxy.
- `app/api/auth/{login,register,refresh,logout}/route.ts` (new) — one action each: validate →
  forward → set cookies. `refresh` also accepts `?next=` and answers `303` to a sanitized internal
  path. `logout` is POST-only and answers 204 with both cookies expired even when auth-svc is down.
- `proxy.ts` (new, repo root) — `GET /api/auth/session` is rewritten to `${AUTH_SVC_URL}/api/v1/auth/me`
  with `Authorization: Bearer <sf_at>` injected server-side and the cookie header deleted, so
  auth-svc never receives a cookie it did not ask for. `/account/*` and `/checkout/*` redirect to
  `/signin?next=…`, or to `/api/auth/refresh?next=…` when only `sf_rt` is present.
- `lib/auth/browser.ts` (new) — `submitAuth(path, body)` → `AuthErrorCode | null`. The only auth
  module a client island imports, and it cannot return a token because it never reads one.
- `SigninForm`/`SignupForm` wired (`router.replace(nextPath); router.refresh()`);
  `signin|signup/page.tsx` pass a sanitized `nextPath`; `ForgotForm`'s TODO retargeted to "auth-svc
  has no reset endpoint".
- `.env.example` (new) — `AUTH_SVC_URL`, `CMS_BASE_URL`, `REVALIDATE_SECRET`.

## Decisions

1. **Four route handlers own the tokens; the browser is never trusted with one.** Any client-side
   store would break the `AGENTS.md` ban on `localStorage` and put a bearer token in reach of an
   XSS. Rejected: keep the token in memory in a React context — it survives exactly one refresh,
   and the ban is on the exposure, not on the storage API.
2. **The proxy forwards one path only.** `/api/auth/session` is a rewrite with an injected header;
   the four actions are ordinary handlers. Putting token building in the proxy as well would mean
   two places know how a session is assembled. Rejected: one catch-all proxy that forwards every
   `/api/auth/*` call — it cannot write `Set-Cookie` on a rewrite the way a handler can.
3. **Refresh is a route, not a proxy rewrite.** It has to *write* two cookies with the storefront's
   own attributes; a pass-through would return auth-svc's `Set-Cookie` with the wrong domain and
   path. Rejected: let the proxy rewrite refresh and forward `Set-Cookie` — the cookie scope then
   depends on a header auth-svc never intended for a third party.
4. **Error text is mapped, never forwarded.** auth-svc has no domain error codes, so
   `INVALID_CREDENTIALS`, `TOKEN_REUSED`, `ACCOUNT_DISABLED` and `SERVICE_UNAVAILABLE` are derived
   from status *and* message. Rejected: render auth-svc's `message` — "security violation" and
   "Account is disabled" are both internal phrasing and one of them is an enumeration oracle.
5. **`safeNextPath` is one function used by three callers.** Rejected: keep the inline regex in the
   page and re-derive it in the refresh route — the second copy is the one that forgets `//`.
6. **Logout is POST-only.** Rejected: a `GET /api/auth/logout` link — `SameSite=Lax` still sends
   cookies on a top-level cross-site GET, so any page could sign a shopper out.
7. **The `remember` checkbox stays cosmetic.** auth-svc fixes 15 m / 30 d server-side; faking a
   longer-lived cookie in the browser would produce a session that looks longer than the token
   actually lives. Rejected: extend `Max-Age` client-side when `remember` is ticked.
8. **`submitAuth` returns a code, never a payload.** Rejected: return the whole `Response` and let
   each form parse it — that is how a token eventually leaks into a client component.

## Verification

| Check | Result |
|---|---|
| `frontend/storefront` `pnpm -s test` | 418 passed (58 files); 80 of them new or rewritten for this task |
| `test/lib/auth/client.test.ts` | 16 cases: session parse, 401 → `INVALID_CREDENTIALS`, 409 → `EMAIL_TAKEN`, 401 "security violation" → `TOKEN_REUSED`, 401 disabled → `ACCOUNT_DISABLED`, 400 → `VALIDATION_FAILED`, abort → `SERVICE_UNAVAILABLE`, 503 → `SERVICE_UNAVAILABLE` |
| `test/lib/auth/session.test.ts` | 7 cases — cookie names, `Max-Age`, `Path=/` vs `Path=/api/auth`, `HttpOnly`, `SameSite=Lax`, `Secure` only in production |
| `test/lib/auth/next.test.ts` | 21 cases — rejects `//evil.com`, `https://…`, `/\evil`, accepts `/checkout`, `/account?tab=1` |
| `test/app/api/auth/*.test.ts` | login 5, refresh 6, logout 3, register 3 — cookie attributes asserted via `getSetCookie()`, and the body is asserted to be exactly `{user}` / `{ok:true}` |
| `test/proxy.test.ts` | 9 cases — session forward injects `Authorization` and strips `cookie`, 401 without `sf_at`, `sf_rt`-only → refresh with a sanitized `next`, pass-through with `sf_at` |
| `test/app/(auth)/auth-forms.test.tsx` (rewritten) | 10 cases against a mocked `fetch`; the two `displayFor`-after-timeout stubs are gone |
| G3 (no-token proof) | `accessToken` appears only in `lib/auth/client.ts`, `lib/auth/session.ts` and `proxy.ts` — **zero occurrences in the four route handlers**, which spread `result.data` straight into `sessionCookies` |
| `tsc --noEmit` | exit 0 |
| `next build` | clean; `ƒ Proxy (Middleware)` detected; all four handlers server-rendered |
| commit | `frontend/storefront` `71f04a5` |

## Open

- `pnpm lint` is broken in this repo and was broken before this task: Next 16 removed
  `next lint`, so the script resolves a `lint/` directory that does not exist. The merge gate for
  this task was `pnpm -s test` + `tsc --noEmit` + `next build`. Adding an ESLint flat config is its
  own task.
- There is no sign-out affordance in the shell. `AccountItem = 'signout'` exists in
  `navSettings.ts`, but the account menu renders no link, so `POST /api/auth/logout` has no caller.
  The menu must post a form (not a link, see decision 6). Logged as a follow-up.
- auth-svc emits no domain error codes, so `TOKEN_REUSED` and `ACCOUNT_DISABLED` are matched on
  message text. That tie breaks the day anyone edits a string in auth-svc; codes in the error
  envelope are the fix, in auth-svc.
- No forgot-password flow exists on either side. `ForgotForm` keeps its stub with a
  `TODO(auth-client)` that names the reason.
