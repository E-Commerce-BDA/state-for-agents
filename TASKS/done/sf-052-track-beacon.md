# sf-052 — storefront page-view beacon (done, 2026-11-23)

## What

Every storefront route now reports a page view, and leaving a page sends one
heartbeat with `exited: true`. The browser only ever calls `/api/track` on this
origin; the BFF forwards to analytics-svc over HTTP. No Kafka client or broker
credential exists in this repo.

## How

- `PageViewTracker` is mounted once in the root layout. It sends a pageview on
  route change and a single exit heartbeat on `pagehide`, guarded by a ref so
  the event cannot double-fire. It uses `sendBeacon`, so the browser queues the
  request and navigation never waits on it.
- `/api/track` validates the body with a strict zod schema, adds the guest
  `sessionId` from `sf_cid` (minting one when the proxy did not — the proxy
  matcher does not include this route), and forwards to analytics-svc. It
  answers 202 even when analytics is down.
- Consent is a pure helper used in both places: Do Not Track, Global Privacy
  Control, and `sf_track_optout=1` all suppress the event. No `userId` is
  forwarded because the storefront never reads one from the access token; the
  payload stays an anonymous session id.
- `analytics` was added to the service registry (port 4060, 2 s timeout) and
  `.env.example`. The client is server-only and constructed per call.

## Decisions (+ one rejected alternative each)

1. **sendBeacon to this origin** — the browser has no service URL to call and
   no reason to know analytics exists. Rejected: a browser-side analytics
   client (would need credentials or a public endpoint).
2. **Always 202** — a tracking outage is not a shopping problem. Rejected:
   surfacing 503, which would make the UI handle an error nobody can act on.
3. **sessionId only, no userId** — C5 wants anonymous session ids; reading the
   JWT on every beacon would add PII and a round trip. Rejected: calling
   `/api/auth/session` per beacon.
4. **`usePathname` + window.location** — `useSearchParams` would force a
   Suspense boundary around the root layout on static routes. Rejected: that
   extra wrapper for a query string the beacon can read itself.

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 1290 tests / 161 files green |
| `npx next build --webpack` | green, `/api/track` registered |

Commits in storefront and Documentation follow this task.
