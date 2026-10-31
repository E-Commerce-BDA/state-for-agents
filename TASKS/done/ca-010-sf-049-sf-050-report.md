# ca-010 + sf-049 + sf-050 — the seam wave: final report

> Tasks: `ca-010` (cart-svc prices add-to-cart from catalog-svc over HTTP), `sf-049`
> (storefront thin auth client and proxy), `sf-050` (storefront CMS reads and the
> revalidate webhook). Written after every gate passed on 2026-10-31.
> Read this with `TASKS/done/ca-010-cart-http-catalog.md`,
> `TASKS/done/sf-049-storefront-auth-client.md` and
> `TASKS/done/sf-050-storefront-cms-revalidate.md`; those carry the file-by-file detail.

## 0. What shipped, in one paragraph each

**`ca-010` — the cart stopped pricing from a fixture.** `HttpCatalogClient` replaced
`FixtureCatalogClient` in production: one batch `GET /api/v1/catalog/internal/products?ids=`
per add-to-cart, authenticated with `x-service-key` and bounded by a 1.5 s abort, parsed
against a local Zod schema that strips unknown keys, and reduced to the **payable** price
(`effectivePrice ?? unitPrice`). Every failure mode answers `503 CATALOG_UNAVAILABLE` and
writes nothing — no cart, no line, no `cart.outbox` row. The fixture survives only as
`catalog.fixture.ts`, injected by each e2e suite, and `CATALOG_SVC_URL` joined the Joi schema
and `.env.example`. 103 unit (15 files) + 99 e2e (12 files, 1 skipped) green, lint 0 over 71
files, build clean.

**`sf-049` — the storefront got an auth client that never leaks a token.** `lib/auth/client.ts`
is the only module that ever holds an `accessToken`/`refreshToken`, and it imports nothing from
framework or browser. Four BFF handlers (`app/api/auth/{login,register,refresh,logout}`) call
auth-svc, turn the pair into `HttpOnly` cookies (`sf_at` 15 min at `Path=/`, `sf_rt` 30 days at
`Path=/api/auth`; `SameSite=Lax`, `Secure` in production) and answer only `{user}` / `{ok:true}`.
`proxy.ts` forwards exactly one path, `GET /api/auth/session` → auth-svc `/me`, injecting the
Bearer server-side and stripping the inbound `Cookie`; it also guards `/account/*` and
`/checkout/*` by bouncing through `/api/auth/refresh` or `/signin` with a `next` value that
passes one shared open-redirect guard. Both auth forms now post to the real endpoints.

**`sf-050` — CMS content became real, and the purge arrow became real with it.** Every read
goes through `lib/cms/{client,tags,navigation,pageSettings}.ts` as
`fetch(url, { next: { tags: [tag], revalidate: 300 } })`, so the Next Data Cache is the shared
layer and the tag is the purge handle; the resolvers cascade `cms-svc → a bounded 32-entry
in-process TTL cache → DEMO_NAV_INPUT` and the root layout has no throwing path. `POST
/api/revalidate` is the CMS→UI arrow: constant-time secret compare (SHA-256 both sides, fails
closed when `REVALIDATE_SECRET` is unset), a tag allowlist shared with the readers, dedupe, and
`revalidateTag(tag, 'max')` per tag. All three `TODO(cms-svc)` null sources in the auth pages are
gone — plus the one in `lib/shell/demoNavInput.ts` — leaving only the pre-existing marker in
`components/shell/SearchMount.tsx`, which is out of this wave's scope.

The wave is **137 new test cases**: 80 auth (client 16, session 7, next-path 21, login 5,
refresh 6, logout 3, register 3, proxy 9, rewritten forms 10) and 57 CMS (client 11, navigation
5, tags 18, cache 8, revalidate 15). The storefront stands at **475 tests in 63 files**.

---

## 1. Architecture decisions, each with the alternative it rejected

| # | Task | Decision | Alternative rejected | Why the rejection lost |
|---|---|---|---|---|
| D1 | `ca-010` | Add-to-cart calls catalog-svc **synchronously**, one request | Keep the fixture behind a flag; read the price from a `product.updated` consumer instead | The fixture is a lie in production. An event-driven price would make add-to-cart return a price the cart cannot yet know, and the first `add` after a cold start would have no price at all |
| D2 | `ca-010` | Price is `effectivePrice ?? unitPrice` — the **payable** price | Store the list price and discount at render; let checkout re-price and accept the difference | order-svc re-prices from the same field, so a list-price cart shows one total and charges another. The cart total is a quote and must quote what will be charged |
| D3 | `ca-010` | A catalog failure is `503 CATALOG_UNAVAILABLE`, never `null` | Map a failed lookup to `null` (which becomes `422 CART_PRODUCT_UNAVAILABLE`) | `422` says "this product does not exist" — a lie the customer retries into. "I could not ask" and "it is gone" must stay distinguishable all the way to the browser |
| D4 | `ca-010` | One attempt, 1.5 s abort, no retry | A retry ladder (1/2/4 s) like the outbox relay | Add-to-cart is interactive: a retry doubles the worst case and the shopper can click again. The outbox's ladder exists because nobody is waiting; here somebody is |
| D5 | `ca-010` | Local Zod schema for the response, unknown keys stripped | Blind TypeScript cast; wait for `@ecom/contracts` response schemas | A wire change must surface as a `503` here, not as `undefined` inside a cart line. Stripping (rather than `strict()`) lets catalog add fields without a cart release |
| D6 | `ca-010` | Fixture moved to `catalog.fixture.ts`, injected by every e2e suite | Delete the fixture; leave it as the default provider | Deleting it would make 12 e2e suites require a live catalog on `:4020` — the fail-closed suites exist precisely to have no catalog |
| D7 | `sf-049` | Four BFF handlers own the tokens; the browser receives `{user}` / `{ok:true}` | Token in React memory/context; `localStorage` | Memory and `localStorage` differ only in lifetime — both are reachable by XSS and both survive one refresh. The only durable win is "no token in JS", which requires the BFF shape |
| D8 | `sf-049` | `proxy.ts` forwards exactly one path, injecting the Bearer and stripping the inbound cookie | A catch-all `/api/auth/*` proxy; refresh done as a rewrite | Only a route handler can write `Set-Cookie` with the storefront's own attributes. Refresh-as-rewrite also sets the cookie on the wrong scope, which is the bug that would have shipped silently |
| D9 | `sf-049` | Access cookie at `Path=/`, refresh cookie at `Path=/api/auth` | Both at `/`; both at `/api/auth` | A 30-day credential must not ride on every asset request; and an access cookie scoped to `/api/auth` would not reach `/account`, so the proxy could never see a session |
| D10 | `sf-049` | Logout is `POST`-only and clears cookies **even when auth-svc is down** | `GET /logout`; fail the logout if revocation fails | `SameSite=Lax` still sends cookies on a top-level cross-site GET, so a `GET` link lets any page sign a shopper out. And a shopper who cannot sign out because a service is down is a support ticket, not a security control |
| D11 | `sf-049` | Classify by status first; message text only as the 401-on-refresh tie-break; never forward auth-svc's message | Render the upstream message; block the task until auth-svc emits domain codes | auth-svc emits exactly one code per status (every 401 is `UNAUTHENTICATED`), and its messages are internal phrasing plus an enumeration oracle on login. One narrow, commented `includes()` is cheaper than an outage |
| D12 | `sf-049` | One shared `safeNextPath` with a route allowlist (`/account`, `/checkout`, `/cart`) | `startsWith("/")`; the per-page regex it replaced | `//evil.com` and `https://evil.com` both look like paths to a naive check. The regex was already duplicated in `signin/page.tsx`, which is the drift the shared module ends |
| D13 | `sf-050` | The Next Data Cache (`next: { tags, revalidate }`) is the cross-request layer; **no Redis client** in the storefront | `ioredis`; no cache at all; `unstable_cache` around the client | Redis gives no purge handle that the webhook can reach for free, and puts a server credential in a public-facing app. No cache means every page render waits on cms-svc |
| D14 | `sf-050` | `cms → 32-entry in-process TTL → DEMO_NAV_INPUT`, and the root layout cannot throw | No fallback; an unbounded `Map`; redirect to an error page on CMS failure | The nav is on every page: a cms-svc restart must degrade the chrome, not blank the site. An unbounded map keyed by page is a leak with a nicer name |
| D15 | `sf-050` | `POST /api/revalidate` is secret-gated and **tag-allowlisted**; `revalidateTag(tag, 'max')` per tag | An open endpoint; a bearer JWT; `revalidatePath('/')`; HMAC over the body | An unvalidated `revalidateTag` is one loop away from flushing the whole cache — a self-inflicted outage. `revalidatePath('/')` is the same outage with one call. A JWT adds a key-distribution problem for one caller. Next 16 also requires the `'max'` argument |
| D16 | `sf-050` | One tag vocabulary module (`lib/cms/tags.ts`) with `isAllowedTag`, shared by readers and the webhook | String literals at both ends | A typo at either end silently disables invalidation *forever* — the failure mode is "content never updates and nothing errors" |
| D17 | `sf-050` | The CMS client returns `null`, and validates only the envelope (`version` is a number, payload is an object) | Throw and let an error boundary catch it; a strict schema in the client | Throwing into the root layout is the blank page D14 exists to prevent. A strict schema here would duplicate what the resolvers already do — every inner field degrades to a builtin on a miss |

### The two genuinely close calls

**Message-text error mapping (D11).** It is the only place in this wave where correctness
depends on a string a different repository controls. `lowered.includes("security violation")`
becomes wrong the day someone edits auth-svc's copy, and it becomes wrong *silently* — the
shopper sees "token expired" and gets bounced to sign-in instead of being told their session
was revoked. The alternative was to not distinguish them at all, which is worse: `TOKEN_REUSED`
means "your session was revoked for a security reason" and `ACCOUNT_DISABLED` means "call
support", and collapsing both into "please sign in again" is how a revoked session looks like a
glitch. Accepted because the blast radius is one UI message and the fix is a one-line deletion
once auth-svc emits domain codes.

**The in-process nav cache (D14).** It is per-replica, it resets on deploy, and it means two
replicas can serve two different navs for up to 300 s after a CMS edit (the Data Cache is
shared, this is not). The alternative — no fallback, or a shared Redis — either blanks the site
during a cms-svc restart or reintroduces the credential and the purge problem. The honest
framing is: this is not a cache, it is a "do not blank the page" store, and it carries the
`stale`/`fallback` flags so a future metrics pass can tell degradation from success.

---

## 2. Trade-offs accepted

1. **Add-to-cart now has an availability dependency on catalog-svc.** It did not before (the
   fixture never failed). The mitigation is the failure *code*, not the dependency: a shopper
   who gets `503 CATALOG_UNAVAILABLE` knows to retry, which is strictly better than adding an
   item at a price that is already wrong.
2. **The cart's price is a snapshot with no expiry.** A price change between add and checkout
   leaves a cart line that quotes the old price; order-svc re-prices and the shopper sees the
   difference at checkout. Storing a `priceCheckedAt` and re-validating on cart read would be
   the fix — it is not in `ca-010`, and nothing currently warns the shopper.
3. **`classify()` ties two error codes to upstream message text** (D11). Documented at the
   call site, and the same comment names the fix.
4. **The nav cache is per-process** (D14). It is a degradation store, not a cache; it is
   labelled that way in code, docs and `tasks.json#follow_ups`.
5. **The revalidate webhook is a static shared secret** (D15). No rotation mechanism, no
   replay protection, no per-caller identity. Acceptable because the only effect is a purge,
   which is idempotent — the worst a replayed request does is re-purge something already cold.
6. **Tag granularity is per page key, not per field.** A theme edit under `cms:global-settings`
   purges the whole theme tag; a nav edit purges `cms:navigation` site-wide. Finer tags would
   mean more tags than there are distinct reads, and every one is a chance to forget an
   invalidation.
7. **The storefront's lint gate is still dead.** Next 16 removed `next lint`, so the gate for
   this wave was `pnpm -s test` + `tsc --noEmit` + `next build`. Six new `lib/` modules and no
   unused-import or dead-code enforcement is a real hole; it is named in §7 of `STATUS.md` and
   in `sf-049`'s follow-ups rather than quietly ignored.
8. **Three degraded paths have no metric**: nav `stale`, nav `fallback`, and the webhook's
   `401`s. The flags exist in the return type, which is the part that had to land now;
   exporting them is observability work recorded as debt in `10.Observability.md`.

---

## 3. Learning outcomes

1. **A cache you cannot purge is a copy you cannot correct.** `next: { revalidate: 300 }`
   renders perfectly on its own — which is exactly the trap: the page looks right, the webhook
   looks redundant, and the tag is the only thing that makes the pull model invalidatable. The
   proof that the tag is really in the Data Cache is not the argument in the source, it is
   `Revalidate 5m` in the build's route table.
2. **Next 16's proxy matcher is parsed at compile time.** A shared `const SESSION_PATH` in
   `matcher` fails the Turbopack build ("need to be static strings"). The constant stays for the
   runtime branch; the matcher must be a literal. Config is not code.
3. **`NextResponse.rewrite(url, { request: { headers } })` replaces the request's headers, it
   does not merge them.** Next transmits `x-middleware-override-headers` and deletes every
   header not listed. That is *why* `headers.delete("cookie")` genuinely strips the cookie —
   and why you must start from a copy of the inbound headers or lose `accept-language`.
4. **A token in memory is not safer than a cookie.** It survives a refresh and is still
   reachable by XSS. "The token is never in JS" is a *shape* decision (BFF handlers own the
   cookies), not a storage decision, and no client-side store can substitute for it.
5. **Cookie `Path` is a security control.** Scoping a 30-day refresh token to `/api/auth` means
   an ordinary page request never carries it. The corollary bit twice: signing out has to clear
   both cookies *with the attributes they were set with*, because a `path` mismatch leaves the
   original alive while the server believes it is signed out.
6. **`SameSite=Lax` does not protect a state change reached by GET.** Cookies ride a top-level
   cross-site navigation, so a `GET`-based logout is a CSRF that works from any page on the
   internet. POST-only was not a style preference.
7. **`timingSafeEqual` throws on unequal lengths.** Hashing both sides first gives two
   fixed-length buffers, so it never throws *and* the length stops leaking. Two problems, one
   line, and the comment has to say so or someone will "simplify" it back.
8. **Fail closed is only half the job; fail with the right code.** Degrading a catalog outage to
   `null` would have produced `422 CART_PRODUCT_UNAVAILABLE` — a message that is true of nothing
   and that the shopper cannot act on. The difference between "it does not exist" and "I could
   not ask" is the whole error design, and it has to survive all the way to the browser copy.
9. **The cart must quote the payable price.** `effectivePrice ?? unitPrice` is one expression
   whose alternative is a customer seeing one total in the cart and another at checkout, because
   order-svc re-prices from the same field.
10. **A bounded cache needs boundary tests, not hit/miss tests.** The cases that fail when
    someone simplifies the implementation are the TTL boundary (a hit at 299 s, a miss at 300 s),
    eviction at exactly the cap, and "re-insert moves the key to the back". Eight cases in
    `cache.test.ts` are almost all boundaries.
11. **Two bugs my own tests caught, both in the test code.** `refresh.test.ts` first passed a
    cookie string where a `Request` belonged, so the route read `request.nextUrl.searchParams`
    off a string; `proxy.test.ts` first asserted the refresh redirect against `REFRESH_PATH`,
    which is the cookie *scope* (`/api/auth`), not the route (`/api/auth/refresh`). The fix for
    the second one was a rename (`REFRESH_ROUTE`), because two constants that differ by purpose
    should not share a shape.
12. **Framework-free modules are what make a cookie testable.** `session.ts` imports no
    `next/headers` and takes no request object, so cookie attributes are asserted with
    `headers.getSetCookie()` in a plain node test. Every `next/server` import would have dragged
    the whole runtime in.
13. **A "no token leaked" claim is a grep, not a test name.** `accessToken` appears in
    `lib/auth/client.ts`, `lib/auth/session.ts`, `proxy.ts` and their tests — and in **zero**
    route handlers, because each handler spreads `result.data` into `sessionCookies` and returns
    a separate body. The test asserts the body's key set; the grep is what makes the claim.

---

## 4. Brainstorming questions for the next phases

1. **What exactly does `cms-007` send?** The webhook takes tags, but the caller knows page keys
   and section ids. Does cms-svc import the tag vocabulary (a cross-repo copy — the drift risk
   D16 exists to prevent), or does the webhook accept `{"pageKey":"auth"}` and build the tag
   itself? The contract is written down; the choice is not made.
2. **Should the revalidate secret be an HMAC over the body?** A static secret authenticates the
   caller but not the payload, and rotation with two replicas is an env change plus a rolling
   restart. HMAC would also mean the allowlist is not the only thing standing between a bug and
   a full cache flush.
3. **Does add-to-cart belong in a server action for `sf-051`?** A client `fetch` has nowhere to
   render `503 CATALOG_UNAVAILABLE` except a toast. A server action would let `sf-051`'s cart
   page show the failure inline — at the cost of the cart page depending on a Next runtime
   feature that is not tested anywhere yet.
4. **Does the cart need to store a price at all?** It could store `priceCheckedAt` and re-read
   the catalog on cart display. Cheaper to be correct, more requests per page, and it makes the
   cart page depend on catalog-svc exactly like add-to-cart now does.
5. **Is the guard's redirect method-aware?** It redirects any method on `/account` or
   `/checkout`; `NextResponse.redirect` answers 307, which keeps the method but loses the body.
   Today nothing posts to a guarded path — `sf-051`'s checkout form will, and "your POST became
   a GET to `/signin`" is a bad first experience. Does the guard need to distinguish navigation
   from mutation?
6. **Should the storefront pin `@ecom/contracts` at all?** It now parses auth-svc's and
   cms-svc's payloads by hand (`asSession`, `asEnvelope`). `sf-053` repins contracts — is the
   point of that repin to replace those two guards with schemas, or only to unblock something
   else?
7. **Where do domain error codes come from?** auth-svc emits one code per status. `TOKEN_REUSED`
   and `ACCOUNT_DISABLED` are the two the storefront cannot do without, and the mapping that
   substitutes for them is the single most brittle line in the wave. Is that `au-005`, or does
   it deserve its own task because it crosses two repos?
8. **Does the shell get a sign-out affordance in `sf-051`?** `POST /api/auth/logout` exists,
   is tested, and nothing calls it. That is not a bug the tests can catch, and it is the kind of
   gap that survives several "green" waves.
9. **One `degraded` counter with a reason label, or one counter per path?** `nav_stale`,
   `nav_fallback`, `catalog_unavailable` and `revalidate_401` are four different decisions:
   the first two say "cms-svc is unwell", the third says "the catalog is unwell", the fourth says
   "someone is probing the webhook". A single counter would hide exactly the distinction that
   matters.
10. **Is `cms:global-settings` premature?** `getGlobalSettings` is implemented, tested, in the
    allowlist — and read at no call site. Either wire the theme read or take the tag out of the
    allowlist; an allowlisted tag nothing reads is an invitation to purge nothing.
11. **When does the storefront's dead `pnpm lint` become a task?** It is pre-existing, it is
    documented, and this wave added six `lib/` modules with no unused-import check. "Pre-existing"
    is a reason to schedule it, not a reason to keep deferring it.
12. **Should the proxy refresh transparently?** Today a shopper with an expired access cookie
    but a live refresh cookie is bounced through `/api/auth/refresh`, which is a redirect per
    15 minutes. Doing the refresh inside the proxy would be invisible but would put a token
    write in the hot path of every guarded navigation. Which cost do we prefer?

---

## 5. Gate evidence

| Gate | Command | Result |
|---|---|---|
| G1 | `cart-svc`: `pnpm lint` / `pnpm test` / `pnpm build` / `pnpm test:e2e` | lint **0 errors** (71 files); **103 passed** (15 files); build exit 0; **99 passed + 1 skipped** (12 files); `http-catalog.client.spec.ts` 12 cases; `catalog-failure.e2e-spec.ts` proves the fail-closed path writes no cart, no line and no outbox row |
| G2 | `frontend/storefront`: `pnpm -s test` / `tsc --noEmit` / `pnpm -s build` | **475 passed in 63 files**; tsc exit 0; build clean, route table shows `Revalidate 5m` and `ƒ Proxy (Middleware)` |
| G2a | the two files written last, in isolation | `cache.test.ts` 8 + `revalidate.test.ts` 15 = **23 passed** before the full run |
| G3 | `grep -r accessToken frontend/storefront --exclude-dir=node_modules` | only `lib/auth/client.ts`, `lib/auth/session.ts`, `proxy.ts` and their specs; **0 route handlers**; each handler's body asserted to exactly `{user}` / `{ok:true}` |
| G4 | `grep -rn "TODO" frontend/storefront/{app,lib,components}` | 4 markers remain across 3 files, all documented and all older than this wave: `ForgotForm.tsx` ×2 (`auth-copy`, `auth-client` — auth-svc has no reset endpoint), `components/shell/SearchMount.tsx` (`cms-svc`, never in the plan's list), `app/components/page.tsx` (`hook-era`). Four of the five `TODO(cms-svc)` markers that existed before the wave are gone — the three auth-page null sources and `lib/shell/demoNavInput.ts` |
| G5 | `node -e` over `tasks.json` (inline, script not committed) | **128 tasks, 96 done / 0 in-progress / 32 todo**, 0 duplicate ids, `byRepo` equals the entries field by field, `summary` equals the computed totals, every done/in-progress `log` resolves inside `TASKS/done/`, no `todo` carries a log |
| G6 | `git status --porcelain` in each of the 12 repos | clean; see §6 for the commit list and the unpushed state |
| packages | `@ecom/contracts` / `@ecom/messaging` resolution | cart-svc unchanged at 1.8.0 / 0.2.0 — `ca-010` touched no dependency |

Two harness facts belong in the evidence rather than a footnote: the **cart-svc e2e run reports
1 skipped file** by default (the gated `RUN_KAFKA_E2E` live spec), so a "green e2e" claim must
name whether the gate was on; and the storefront's `pnpm -s build` output is the only place the
Data Cache configuration is observable, which is why the route table is quoted above instead of
the source line.

---

## 6. Handoff

- **Four commits, one per repo, all local-only.** `cart-svc` **`cb305e7`** (`ca-010`),
  `frontend/storefront` **`71f04a5`** (`sf-049`) and **`5de7d95`** (`sf-050`), `Documentation`
  **`40348b9`** (6 files, +135/−8). `state-for-agents` carries this tracker commit, which cannot
  record its own hash.
- **Nothing was pushed, tagged, released or published.** Recomputed with `git rev-parse @{u}` +
  `git rev-list --count @{u}..HEAD`: `cart-svc` ahead 1, `frontend/storefront` ahead 2 (upstream
  `origin/staging`), `Documentation` ahead 1, `ecom-infra` 5 with no upstream at all, and
  `ecom-messaging` 1 with no remote. Everything else is level with its upstream. The wave-2
  commits that were local-only last pass reached their remotes at 18:18 through an out-of-band
  step, not through this plan.
- **P2 is 8/10.** `sf-051` (commerce routes and components) and `cat-011` are what close it.
  `cms-007` now has a written contract to call — `POST /api/revalidate` with
  `x-revalidate-secret` and `{"tags":[…]}` — and `cms-006` still owes the `media.tasks` → SQS
  move.
- **The §4 questions are not blockers.** §4.5 (a method-aware guard) becomes one the moment
  `sf-051` adds a checkout form; §4.7 (domain error codes) is the one debt in this wave that
  touches another repository's contract; §4.8 (no sign-out affordance) is the only item here
  that is a user-visible gap rather than an internal one.
- **If you inherit this and only read one thing:** `lib/cms/client.ts` and `lib/auth/session.ts`
  are the two modules whose comments carry the reasoning the tests cannot. Every other file in
  the wave is mechanical by comparison.
