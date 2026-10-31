# sf-050 — storefront: CMS reads and the revalidate webhook (done, 2026-10-31)

## What

Every storefront surface that is supposed to be CMS-driven was rendering a built-in default: the
navbar read `DEMO_NAV_INPUT` in `app/layout.tsx`, and the three auth pages passed
`source: { fetchPage: async () => null }`. cms-svc was running and reachable and nothing read it.
This task makes the storefront a reader of cms-svc, adds the one arrow that lets a CMS edit reach
the Next Data Cache (`POST /api/revalidate`), and guarantees that a cms-svc outage degrades to the
last known value instead of a blank navbar on every route.

## How

- `lib/cms/tags.ts` (new) — the tag vocabulary both sides use: `cms:page-settings:<key>`,
  `cms:global-settings`, `cms:navigation`, plus `isAllowedTag` / `isPageKey`
  (`[a-z0-9-]{1,32}`) which is the allowlist `POST /api/revalidate` enforces.
- `lib/cms/client.ts` (new, pure) — `createCmsClient({ baseUrl, fetchFn, timeoutMs = 2000 })` with
  `getPageSettings`, `getGlobalSettings`, `getNavigation`. Every call is
  `fetch(url, { signal, next: { tags: [tag], revalidate: 300 } })` and resolves to `null` on a
  non-2xx, a timeout, a non-JSON body or a malformed envelope. `getPageSettings` refuses a page key
  that is not `isPageKey` *before* it becomes a path segment.
- `lib/cms/cache.ts` (new) — `createMemoryCache<T>({ maxEntries = 32, now })`, a TTL map with
  insertion-order eviction; `get` drops an expired entry, `set` moves a re-inserted key to the back.
- `lib/cms/navigation.ts` (new) — `fetchNavSettings({ source, cache })` cascade: cms-svc → the
  stale memory entry → `DEMO_NAV_INPUT`, returning `{settings, version, stale, fallback}`.
- `lib/cms/pageSettings.ts` (new) — `fetchAuthPageSettings(pageKey)`, one helper replacing three
  copies of the same no-op deps.
- `lib/cms/authSettings.ts` — the CMS source now sends `next: { tags: [cmsTag.pageSettings(key)],
  revalidate: CMS_REVALIDATE_SECONDS }`, so a revalidate actually drops the entry it cached.
- `app/api/revalidate/route.ts` (new) — `POST`, `x-revalidate-secret`, constant-time compare on the
  SHA-256 of both sides, allowlist, then `revalidateTag(tag, 'max')` per tag; `401 UNAUTHORIZED`,
  `400 INVALID_TAGS`, `200 {revalidated, now}`. Fails closed when `REVALIDATE_SECRET` is unset.
- Call sites: `app/layout.tsx` (`DEMO_NAV_INPUT` → `await fetchNavSettings()`),
  `signin|signup|forgot/page.tsx` (`fetchAuthPageSettings("auth")`); all four `TODO(cms-svc)`
  markers are gone. `lib/shell/demoNavInput.ts` stays, re-headed as the documented fallback.

## Decisions

1. **The Next Data Cache is the cross-request layer; no Redis in the UI.** `next: { tags,
   revalidate: 300 }` gives a shared cache, a purge handle and a staleness bound in one argument.
   Rejected: add `ioredis` to the storefront — a second cache with no purge handle, and a Redis
   credential in the repo that serves public pages.
2. **A bounded 32-entry map is the *fallback*, not the cache.** It exists only so "cms-svc blipped"
   does not become "navbar blank on every route". Rejected: no fallback at all (a one-second CMS
   restart would blank the chrome store-wide), and an unbounded map (a memory leak keyed by page).
3. **Navigation degrades to the demo input, never to an exception.** The root layout is the one
   component whose failure blanks every route, so `fetchNavSettings` has no throwing path.
   Rejected: `redirect('/error')` on CMS failure — the storefront would be down whenever the CMS is.
4. **The webhook is gated by a shared secret, and fails closed without one.** Rejected: an open
   endpoint (one loop flushes the entire cache — a self-inflicted DoS) and a bearer JWT (the caller
   is a service, not a user; the storefront has no identity to validate).
5. **Constant-time compare on SHA-256 of both sides.** `timingSafeEqual` throws on unequal lengths,
   so hashing first makes length a non-issue and removes the length side-channel with it. Rejected:
   compare lengths then `timingSafeEqual` (two ways to leak), and `===` (leaks a prefix by timing).
6. **The tag allowlist lives in `lib/cms/tags.ts`, shared by readers and the webhook.** A typo in
   one side would otherwise silently disable invalidation forever — nothing would fail, the cache
   would just stop purging. Rejected: string literals at both ends.
7. **`revalidateTag(tag, 'max')` per tag, never `revalidatePath('/')`.** Rejected:
   `revalidatePath` — it drops the whole route tree for the sake of one navbar field, and in Next
   16 the profile argument is required anyway.
8. **Local structural guards instead of `@ecom/contracts` response schemas.** The repo is pinned to
   1.7.0, whose tarball does not export the `settings`/`theme`/`navbar` response schemas; the repin
   is sf-053's job and this task assumes no contracts change. The guards validate only the envelope
   (object payload + numeric version) because the resolvers already degrade every inner field.
   Rejected: repin contracts inside sf-050 — a cross-repo version bump hidden in a UI task.

## Verification

| Check | Result |
|---|---|
| `frontend/storefront` `pnpm -s test` | 475 passed (63 files); 57 of them new for this task |
| `test/lib/cms/client.test.ts` | 11 cases — the three documented URLs, `next.tags` + `revalidate: 300` present in the init, abort signal, bad page key never reaches `fetch`, non-2xx / abort / non-JSON / missing key / string payload / non-numeric version → `null` |
| `test/lib/cms/navigation.test.ts` | 5 cases — CMS up fills the cache and resolves, CMS down serves the stale entry (`stale: true`), no source and no cache → `DEMO_NAV_INPUT` with `fallback: true`, a `null` read treated exactly like a failure |
| `test/lib/cms/tags.test.ts` | 18 cases — the three tag builders, `isPageKey` rejects uppercase / path-shaped / oversize keys, `isAllowedTag` accepts the three shapes and rejects empty, wrong prefix, traversal, trailing space and non-strings |
| `test/lib/cms/cache.test.ts` | 8 cases — TTL expiry at the boundary with an injected clock, expired-on-read eviction, zero TTL ≠ immortal, cap eviction, re-insert moves the key back, default 32, clamped options |
| `test/app/api/revalidate.test.ts` | 15 cases (`vi.mock('next/cache')`) — 401 for absent / wrong / unset-secret **with `revalidateTag` not called**, 400 for 8 malformed tag payloads and for unparseable JSON, 200 calls `revalidateTag(tag,'max')` once per tag, dedupes repeats, response never echoes the secret |
| `tsc --noEmit` | exit 0 |
| `next build` | clean; `/api/revalidate` is a server handler and the routes now report `Revalidate 5m` in the build table |
| G4 (TODO sweep) | the three `TODO(cms-svc)` markers in the auth pages are gone; `lib/shell/demoNavInput.ts` is the documented fallback; the only remaining markers are `ForgotForm`'s two (auth-copy, auth-client), `SearchMount.tsx`'s `TODO(cms-svc)` for curated/trending props and `app/components/page.tsx`'s `TODO(hook-era)` — the last two pre-date this task and are reported, not fixed |
| commit | `frontend/storefront` `5de7d95` |

## Open

- Hand-off for `cms-007` (verbatim, so the caller is mechanical):
  `POST /api/revalidate`, header `x-revalidate-secret: $REVALIDATE_SECRET`, body
  `{"tags":["cms:navigation"]}` or `{"tags":["cms:page-settings:auth"]}`, `200
  {"revalidated":[...],"now":<epoch ms>}`, `400 {"error":{"code":"INVALID_TAGS"}}`,
  `401 {"error":{"code":"UNAUTHORIZED"}}`. Nothing calls it yet.
- The 32-entry fallback cache is per-process and per-instance. With N Next instances a CMS outage
  degrades differently on each one; that is acceptable for a stale fallback and unacceptable if it
  ever becomes the primary cache.
- No metric on `fallback: true` / `stale: true` yet — the storefront has no metrics endpoint.
  Recorded as observability debt in `Documentation/10.Observability.md`.
- The `theme` endpoint (`getGlobalSettings`) is implemented and tested but not read at any call
  site: no storefront surface applies CMS theme tokens yet.
- `lib/cms/authSettings.ts` keeps its own `AuthSettingsCache` injection; `TtlCache<T>` is
  structurally identical, so the two can be merged when someone needs to, not before.
