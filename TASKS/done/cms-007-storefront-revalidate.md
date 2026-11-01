# cms-007 — revalidate the storefront after a content publish (done, 2026-11-01)

## What

The storefront caches CMS reads in Next's Data Cache, which lives in its own process.
`sf-050` built the receiving end — `POST /api/revalidate` behind a shared secret with an
allowlist of tags — and nothing had ever called it. A theme change or a navigation edit
therefore stayed stale until a TTL expired.

cms-007 adds the caller and wires it into exactly the three mutations the storefront
reads today. The tracker had this as `kind: docs`; it is a feature, and the entry was
corrected in the same commit.

## How

- `cms-svc/src/revalidate/revalidate.service.ts` (new) — `revalidate(tags)` POSTs
  `${STOREFRONT_URL}/api/revalidate` with `x-revalidate-secret` and `{ tags }`, bounded
  by `AbortSignal.timeout(2000)`. No secret ⇒ one debug line and the `disabled` counter;
  any failure ⇒ one warn line and the `failed` counter; never a throw. `storefrontTags`
  is the typed list of the three tags this service may send.
- `cms-svc/src/revalidate/revalidate.module.ts` (new) — `@Global()`, so the three
  mutations take it as a collaborator rather than each importing the module.
- `cms-svc/src/settings/settings.service.ts` — `updateGlobalTheme` sends
  `cms:global-settings`; `updatePageSettings(pageKey)` sends
  `cms:page-settings:<pageKey>`; both after the Redis delete.
- `cms-svc/src/navigation/navigation.service.ts` — `updateNavigation` sends
  `cms:navigation` (the widest tag, because the header is on every page).
- `cms-svc/src/app.module.ts` — `RevalidateModule`.
- `cms-svc/src/config/env.validation.ts` — `STOREFRONT_URL` (http(s) URL, default
  `http://localhost:3000`) and `REVALIDATE_SECRET` (`.empty('')`, required and ≥16
  characters when `NODE_ENV=production`, optional otherwise).
- `cms-svc/.env.example` / `.env` — both variables, with the development placeholder
  the storefront's own `.env.example` uses, and a note that the pair must match
  byte-for-byte.
- `cms-svc/test/setup-env.ts` — `REVALIDATE_SECRET = ''`, so every settings/navigation
  e2e stops depending on something listening on `:3000`.
- Tests: `revalidate.service.spec.ts` (10 cases), `settings.service.spec.ts` and
  `navigation.service.spec.ts` (exact tag assertions), `test/revalidate.e2e-spec.ts`
  (5 cases against a `node:http` stub that records path, method, header and body).
- Docs: `Documentation/1.Architecture.md` §6.5, `Documentation/services/cms.md`,
  `cms-svc/README.md`, and the corrected "cms-svc consumes product.imported" claim in
  `Documentation/0.Project-Overview.md`.

## Decisions (+ one rejected alternative each)

1. **Only the three tags the storefront can accept.** `lib/cms/tags.ts` allows
   `cms:global-settings`, `cms:navigation` and `cms:page-settings:<pageKey>`; anything
   else is rejected with `400 INVALID_TAGS`. Sections, pages and blogs send nothing and
   that is recorded rather than papered over — there is no storefront reader for them
   yet (`sf-061`/`sf-062`). Rejected: invent a `cms:sections` tag now, which the
   storefront would answer with a 400 and a warn line on every publish.
2. **Best-effort, never a failed write.** The write has already committed when the call
   is made, so the worst case must be staleness for one TTL, never a 500 to the editor.
   Rejected: a durable revalidation queue — a new relay and a second failure domain to
   avoid one TTL of staleness.
3. **Two seconds and a counter.** An unbounded or long timeout would let a slow
   storefront hold a CMS request. Rejected: reuse the HTTP client's default timeout,
   which is tuned for service-to-service calls, not for a cache hint.
4. **Production refuses to boot without the secret.** A production cms-svc whose
   invalidations silently do nothing would serve stale pages forever with no signal.
   Rejected: warn-only on a missing secret.
5. **The e2e suite blanks the secret.** `ConfigModule` never overwrites a variable that
   is already in `process.env`, so an empty string in `test/setup-env.ts` beats `.env`
   and keeps the suites from posting to a real storefront. Rejected: point
   `STOREFRONT_URL` at a closed port and assert the warn line in every suite.

## Verification

| Check | Result |
|---|---|
| `cms-svc` `pnpm test` | 149 passed (22 files) |
| `cms-svc` `revalidate.service.spec.ts` | 10 cases: no secret → no fetch + `disabled`, blank secret treated as unconfigured, exact URL/header/body/signal + `sent`, trailing slash trimmed, default base URL, 500 → `failed` without throw, timeout → `failed`, unreachable → `failed`, tag array copied, timeout constant is 2000 |
| `cms-svc` `settings.service.spec.ts` / `navigation.service.spec.ts` | exact tag lists `['cms:global-settings']`, `['cms:page-settings:signin']`, `['cms:navigation']` |
| `cms-svc` `test/revalidate.e2e-spec.ts` | 5 cases against a stub storefront: the three mutations send their tag, a sections publish sends nothing, a 500 from the storefront still returns 200 from the CMS |
| `cms-svc` `pnpm test:e2e` | 87 passed, 4 skipped (9 files passed, 2 skipped) |
| `cms-svc` `pnpm lint` / `pnpm build` / `pnpm typecheck` | 0/0 on 100 files / clean / exit 0 |
| commit | `cms-svc` `fd02481`, docs `4d3149e` |

## Open

- Sections, pages and blogs send no tag until the storefront has a reader for them and
  a matching entry in `lib/cms/tags.ts`.
- A `REVALIDATE_SECRET` that does not match the storefront's is a `401` and one warn
  line per publish; nothing retries it.
