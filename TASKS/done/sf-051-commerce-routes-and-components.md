# sf-051 — commerce routes on one service seam: final report

> Task: `sf-051` (storefront: commerce routes and components). Written in the
> tracker commit that closes it, after G1–G3 and G5–G8 passed and after the live
> gate G4 was run or recorded as deferred with the reason stated below.
> Read this with the plan it executes ("Commerce routes on one service seam",
> 19 commits) and with `TASKS/done/sf-049-storefront-auth-client.md` /
> `sf-050-storefront-cms-revalidate.md` — those two built the seam pattern this
> one generalises. The money fix that landed mid-wave is ADR 41/42's work:
> order-svc `880af5d` + `728e130`, contracts `08e930c`, storefront `13b1b07`.

## 0. What shipped, in one paragraph each

**The seam.** `lib/services/urls.ts` is now the only place a service base URL is
read (`AUTH/CART/CATALOG/ORDER/CMS_SVC_URL`); `lib/http/result.ts` defines
`ServiceResult<T>` — `{ok:true; data} | {ok:false; kind; status; code; message}`
with an eight-value `kind` taxonomy — and the two transports implement it once:
`lib/http/client.ts` (server-only, timeout, envelope parse, zod check, **never
throws**) and `lib/http/browser.ts` (`bff()` — same-origin, minted
`x-idempotency-key` once per logical mutation, single-flight 401 refresh, one
replay). Every earlier one-off (auth's four handlers, cms's tagged fetches) keeps
working; nothing was rewritten to the new seam out of scope.

**Clients and schemas.** `lib/{catalog,cart,order}/{schemas,client}.ts` —
catalog list/detail/categories with `status:"active"` hard-coded in the client
(a caller param can leak drafts), cart full-reconcile responses, order
checkout/getOrder/listOrders. Response shapes are local zod objects with loose
inner fields: a blind cast breaks silently, a `.strict()` schema breaks on any
upstream addition, and the storefront pins contracts 1.7.0 (sf-053 owns the
repin, so the schemas live here until then).

**Identity.** `sf_cid` (guest cart id) is minted in `proxy.ts` when absent, with
a BFF fallback for direct API hits; the pattern is validated before it is
written. Login and register handlers merge the guest cart **server-side** after
the cookies are set, never block login on merge failure, and rotate `sf_cid` on
success so a later sign-out cannot reuse a converted cart. The browser never
calls merge.

**BFF handlers.** `app/api/{cart,...,checkout,orders/[id],account}` —
same-origin guard (403 cross-origin), `no-store` on everything private,
`requireIdempotencyKey` (400 without it on checkout), pass-through of upstream
status/code. `/api/account` is a fan-out (auth `/me` + order list in parallel)
with partial degradation: an orders failure yields `[]` plus an `ordersError`
flag, not a blank page.

**Five routes + home.** `/products` (render-dynamic on `searchParams`, catalog
fetched in RSC, cached 60 s), `/products/[slug]` (ISR 60, `generateMetadata`,
PurchasePanel island, related-by-category), `/cart`, `/checkout` (+
`/checkout/confirmation/[orderId]`), `/account` (all static shells,
client-rendered private data), and `/` (HeroSection + FeaturedGrid: the 8 newest
products until the CMS-driven strip lands as sf-060). `app/page.tsx`'s
"under construction" placeholder is deleted; `app/(shop)/layout.tsx` carries the
container.

**Blocks and islands.** QuantityStepper, EmptyState, Gallery, VariantSelector,
ProductGrid, HeroSection, PageHeader, CartLineItem, MiniCartDrawer — dumb blocks
in `components/`, state-owning islands in `app/(shop)/_components/`; `Navbar`
dropped its hardcoded disabled cart button and `NavbarMount` feeds it
`useCart()`. `lib/commerce/{quantity,gallery,variants,fromCatalog}.ts` own the
pure models (clamps, primary-first image order, impossible-combination pruning,
card mapping).

**Client cart store.** `lib/cart/state.ts` is a pure reducer
(`emptyCart/applyAdd/applyQty/applyRemove/reconcile/toView`), `CartProvider` is
the only React context in the path (optimistic mutations → BFF → revert + Toast
on failure), `lib/cart/port.ts` maps transport kinds to QuickAdd outcomes
(422 → `"out-of-stock"`, 503/network → `"unavailable"`, abort → `"aborted"`).
`createDemoQuickAdd` survives only in the `/components` showcase.

**Money, fixed at the source.** The wave began with order rows typing money as
`string | number` and a `lib/money.ts` normalizer on the consumer side. That was
the wrong end. order-svc now parses `DECIMAL` to numbers at the DB boundary
(`880af5d`), `@ecom/contracts` 1.10.0 narrows `moneySchema` to
`z.number().nonnegative()` (`08e930c`, tarball + CHANGELOG + spec), order-svc
repinned to 1.10.0 (`728e130`), and the storefront normalizer was deleted
(`13b1b07`). Three schemas then read `z.number()` for money with no coercion
anywhere in the path.

The suite went **63 files / 475 tests → 116 files / 904 tests** across the wave
— every layer in plan §12 has its file: transport tables, client URL/identity
assertions, BFF handler contracts, block style contracts, pure models, and the
islands' failure paths.

---

## 1. Architecture decisions, each with the alternative it rejected

| # | Decision | Alternative rejected | Why the rejection lost |
|---|---|---|---|
| D1 | Registry + two transports, one `ServiceResult` union | Per-client plumbing (copy `createCmsClient` three more times) | Five call sites, one URL story; three copies of timeout/parse/error handling is three places for the same bug |
| D2 | No retries in the transport | Silent GET retries | Retries hide latency and double-POST mutations; the island owns retry because only it knows whether the operation is safe to repeat |
| D3 | `status:"active"` hard-coded in the catalog client | A caller-supplied status param | One caller that forgets the param ships draft and archived products to shoppers |
| D4 | Private routes client-rendered against the BFF | RSC + `cookies()` on cart/checkout/account | `5.Features.md` §950 mandates private data never cached; cookies() forces every route dynamic and duplicates cart state between server and store |
| D5 | Catalog fetched in RSC, never through the BFF | A catalog BFF hop | SEO plus one fewer hop; the BFF becomes necessary only when load-more append needs client pagination (sf-054) |
| D6 | Time-based `revalidate: 60` only, no tags | Tag-based invalidation now | Tags with no invalidator are decoration; the vocabulary and the caller arrive together in sf-061 |
| D7 | React context + pure reducer for the cart | Zustand | One provider does not justify a dependency; the reducer being pure makes every transition node-testable without React |
| D8 | Identity read from the request object, never `next/headers` | `cookies()` inside handlers | Handler tests would mock the framework; with a request param they are plain functions, and the guard logic is shared and unit-tested |
| D9 | `sf_cid` minted in the proxy, BFF fallback | Mint-on-first-write | Two adds before the first response lands would orphan one cart and silently lose an item |
| D10 | Merge inside login/register; rotate after success | Client-side merge; keep the converted id | The browser must never merge (A4.6); a kept id lets a later sign-out reuse a converted cart |
| D11 | `POST /api/checkout` forwards the caller's key; client mints per body | Server-minted keys | A network retry under a server-minted key creates a second order; the `{key, bodyHash}` pair keeps the key across same-body retries and mints fresh when the body changes |
| D12 | Single-flight refresh on 401 | Parallel refreshes | Concurrent refreshes trip auth-svc's reuse detection and log the shopper out mid-checkout |
| D13 | 409 stock errors reported generically + "review cart" | Parse `message` / fake item attribution | order-svc's 409 carries no item ids; guessing which line failed is worse than asking the shopper to review. Backend change recorded in sf-058 |
| D14 | MiniCartDrawer standalone (Escape/overlay/focus restore) | A `Dialog` variant with `placement` | Adding a placement prop to a shipped primitive drags five artifacts of that primitive into a cart task |
| D15 | `(shop)` group islands in `app/(shop)/_components/` | Shared islands under `components/<domain>` | `components/` is dumb-only by AGENTS.md; group-scoped islands keep the fetch/state wiring out of the primitive library |
| D16 | Local zod schemas, loose objects | Blind casts; `.strict()` responses | Casts break silently on drift; strict breaks on additive upstream fields; the parse logs the mismatch and returns `contract` — loud, degraded, not blank |
| D17 | Plain `<img loading="lazy">` | `next/image` + `remotePatterns` | Image hosts are admin-controlled and unknown at build time; the ProductCard precedent already accepted this |
| D18 | `CartTotals` stays inline CSS | A shared totals component | Two surfaces with different density; a shared block would need a variant prop for 20 lines of markup |
| D19 | Money normalised at the producer's DB boundary, not the consumer | Keep `lib/money.ts` parsing `string \| number` forever | The consumer-side patch is how five services each invented their own parser. Fixing the source let three schemas collapse to `z.number()` and deleted the normalizer (ADR 41/42) |
| D20 | Contracts pin untouched during the wave (sf-053 owns the repin) | Bump 1.7.0 → current inside sf-051 | A version bump with its own migration story is a second task; dragging it in would have made the route work unreviewable. (The money fix was the one exception, and it got its own commits in its own repos.) |

### The two genuinely close calls

**Generic 409 versus attributed 409 (D13).** The honest-looking alternative was to
parse the upstream message for product ids and highlight the failing lines. It lost
because the message is not a contract: order-svc's 409 has no `details` field, so
attribution would be regex against prose that can change in any release. A wrong
attribution ("Mug is out of stock" when it was the Plate) costs more trust than a
generic banner. The accepted cost — the shopper re-checks the cart — is one tap.

**Minting the idempotency key per body versus per attempt (D11).** Per-attempt
mints are simpler and wrong: every retry of the *same* submission becomes a new
order, which is the exact failure the key exists to prevent. Per-body keeps one
logical attempt idempotent while a *changed* body (the shopper edited the address)
correctly starts a new attempt. The FNV-1a hash over the canonically sorted JSON is
why `canonicalBody` exists; a cryptographic hash would too, but this is a
deduplication discriminator, not a security boundary.

---

## 2. Trade-offs accepted

1. **Response schemas live in the storefront, duplicated against contracts.**
   sf-053's repin deletes them; until then a field rename in order-svc shows up as
   a `contract` failure at runtime rather than a compile error. Local zod with
   degrade-on-parse-failure was chosen over that being invisible.
2. **No per-line stock attribution on checkout 409** (D13). The cart is untouched
   and the message says "review cart"; the precise line waits for sf-058 and the
   backend change it names.
3. **Cart totals lag by one `order.created` round trip.** cart-svc converts
   asynchronously, so the drawer may briefly show pre-checkout lines. The
   confirmation island refreshes once; a polling reconciler was not built.
4. **Home strip is "8 newest", not curated.** The catalog has no `featured` flag
   and the CMS section model is sf-060's job; the heading says "New arrivals" so
   the strip does not claim curation it cannot do.
5. **Debounced quantity has no in-flight lock across lines.** Each line's timer is
   independent; two fast edits on *different* lines issue two requests. Within one
   line the latest draft wins. `inFlight` shows per-line pending state; nothing
   prevents a remove while a qty timer runs (clearing the timer on remove is the
   one guard, and it is there).
6. **`/components` keeps `createDemoQuickAdd`.** The showcase still fabricates
   adds. The rule is now enforced by grep (G5) rather than deletion — the showcase
   is demo surface, the commerce path is not.
7. **`useSearchParams()` islands sit behind `<Suspense>`.** PDP stays static; the
   cost is a fallback frame on variant-driven segments, which the PurchasePanel
   hides by rendering the server-provided default first.
8. **The BFF is a thin pass-through, not an aggregation layer.** Cart mutations
   round-trip browser → Next → cart-svc; one hop more than a direct client call,
   bought entirely for the cookie/identity seam (D8/D9) and same-origin guard.
9. **`sf_cid` rotation on merge is best-effort.** If rotation fails after a
   successful merge the old guest id lingers until the cookie's own expiry; the
   merged cart is already safe, which is why this is a trade-off and not a bug.
10. **Style contracts are paint-only.** Blocks may not emit literal colors/shadows;
    the `-style.test.ts` files assert paint flows through CSS variables, but the
    tests do not catch a wrong *value* — that stays a design-review concern.

---

## 3. Learning outcomes

1. **A debounce composed on a controlled stepper needs a live source of truth.**
   Reading the qty from the timer's captured closure loses taps: two clicks before
   a re-render both report `value+1` against the *old* value. The fix is a ref
   updated synchronously on every change, read at fire time — and a test that
   flushes React between clicks (`act(() => advance(50))`) rather than batching
   both into one act.
2. **A prop contract is a signature, not a vibe.** The three-parameter
   `changeQty(itemId, next, rendered)` died because `CartLineItem.onQty` is
   `(itemId, qty) => void` — the wrapper's third argument was always `undefined`.
   The debug trace that ended the saga read as `next= i1 rendered=` (empty):
   mismatched arity fails silently at the boundary that looks most obvious.
3. **`ServiceResult` never throwing is what makes the islands testable.** Every
   failure path is a value — `{ok:false, kind:"unavailable"}` — so a test asserts
   a banner instead of mocking a thrown-exception maze, and "no blank page" is a
   type-level property, not a code-review habit.
4. **Idempotency belongs to the logical mutation, not the HTTP call.** The
   `{key, bodyHash}` pair encodes that in one type. A key per fetch and a key per
   session are both wrong in opposite directions (double order / lost order).
5. **Framework-free handler inputs pay for themselves.** Passing
   `{req, identity}` into BFF logic (D8) means the handler tests need no Next
   mocks at all — same-origin 403, missing-key 400 and pass-through status are all
   plain function assertions.
6. **Consumer-side patches mark the place where a producer bug lives.**
   `lib/money.ts` was a permanent TODO pretending to be a util. Deleting it and
   fixing order-svc's `DECIMAL` parse closed the class, not the instance — three
   schemas now say `z.number()` and nothing coerces.
7. **Next 16's Promise `searchParams` and static-render constraints surface at
   build, not runtime.** `useSearchParams()` without `<Suspense>` fails the build;
   deleting a page leaves a stale `.next/types/validator.ts` reference until a
   rebuild — generated types are part of the gate, not incidental output.
8. **A fan-out endpoint degrades per-section or it degrades the whole page.**
   `/api/account` returning `{user, orders: [], ordersError: true}` is what lets
   the island show a profile while order-svc is down.
9. **Test fixtures teach arithmetic lessons.** Two fixture lines totalling `$10`
   (1×10 and 2×5) broke `getByText("$10")` — ambiguous matches are a *good* catch
   from RTL, and the assertion belongs on `getAllByText(...).toHaveLength(2)`.
10. **"Registered, not hidden" is a tracker feature.** The wave's deferrals became
    eight tasks with `dependsOn` in the same commit that closed sf-051, so the
    backlog grows *before* the celebration, not after.

---

## 4. Brainstorming questions for the next phases

1. **Does the catalog BFF arrive with sf-054, or does load-more hit the RSC cache
   with a cursor param?** D5 deferred the question; the answer decides whether
   `lib/services/urls.ts` grows a public catalog path or the listing stops being
   pure RSC.
2. **What is the reconciliation policy when cart-svc converts asynchronously?**
   Trade-off 3 accepts a lag. Should the confirmation island poll
   `GET /api/cart` until the lines clear, or should cart-svc's response to
   checkout already carry "converted" state?
3. **Is per-line stock attribution a 409-payload change or a pre-checkout
   validate endpoint?** sf-058 names the former; the latter (dry-run checkout)
   would also catch price drift before payment. Which does order-svc owe?
4. **When does the cart store graduate from context to a real state lib?** D7 said
   "not for one provider". sf-056/057/058 all add client state (wishlist, coupons,
   batch-select); the third non-cart island in `useCart()`-adjacent context is the
   trigger to revisit.
5. **Should `sf_cid` be HttpOnly?** It is read by the BFF only; the browser JS
   never needs it. Making it HttpOnly removes XSS exfiltration of a cart id — at
   the cost of the proxy/BFF being the *only* mint path. Nobody asked before this
   wave shipped it readable.
6. **Who invalidates the PDP ISR (60 s) when the admin edits a product?** sf-061
   answers list/PDP via `POST /api/revalidate` with `catalog:*` tags; does the
   price display get the same treatment or is 60 s of stale price acceptable at
   launch (checkout recomputes anyway)?
7. **Does GuestIdentity deserve a session module of its own once
   `lib/session/` also holds auth-cookie helpers?** Two identity stories
   (`sf_at`/`sf_rt` from sf-049, `sf_cid` here) currently live in different files
   with different owners.
8. **What is the story for the `/components` showcase as blocks multiply?** G5
   keeps demo code out of the commerce path; nothing yet forces showcase
   coverage *when* a new block ships — the style-contract files are hand-written.
9. **Do the eight deferred tasks need a wave order?** They all hang off sf-051;
   sf-058 depends on sf-057, sf-060 on sf-053. A P2-close wave (054/055/056/057)
   followed by a depth wave (058/059) is the implicit shape — is it explicit
   anywhere besides this paragraph?
10. **How much of the checkout copy table is a contract?** `describeFailure` maps
    code families to copy. If order-svc renames `RESERVATION_EXPIRED` the mapping
    silently degrades to the fallback banner. Should the code families be in
    contracts (ec train) rather than in a storefront switch?

---

## 5. Gate evidence

| Gate | Command | Result |
|---|---|---|
| G1 | `pnpm -s test` (frontend/storefront) | **116 files / 904 tests passed** (wave start: 63 files / 475 tests); vitest, node env default + per-file jsdom, no jest-dom |
| G2 | `npx tsc --noEmit` | exit 0, no errors |
| G3 | `pnpm -s build` (`next build`) | clean; `/`, `/products`, `/products/[slug]` (ISR 60), `/cart`, `/checkout`, `/checkout/confirmation/[orderId]`, `/account` in the route table; proxy detected. Also re-ran after C19 to regenerate `.next/types` |
| G4 | live: infra + 5 services + storefront (port 3002), driver `g4.mjs` | **ALL 14 CHECKS GREEN.** `/` hero+New arrivals, `/products` listing, `/products/[slug]` detail, guest cart add 201, register→login→merge (sf_cid rotated, cart preserved), checkout 201 with orderId, idempotent replay same orderId, `GET /api/orders/[id]` schema-validated 200, over-stock 409 INSUFFICIENT_STOCK, signed-out /checkout 307→/signin, `GET /api/account` fan-out 200. Fixes landed: auth-client register→login two-step (`edc8bcf`), status_history schema matched DB columns (`edc8bcf`). |
| G5 | grep over the commerce path | `createDemoQuickAdd` appears only under `/components`; no `TODO`/`coming soon` in `app/(shop)`, `app/api`, `lib/cart`, `lib/checkout`, `lib/commerce`, `lib/http`, `lib/services`, `lib/session`, `lib/{catalog,cart,order}` |
| G6 | `git status` per repo | storefront staging clean, **22 commits unpushed** (`origin/staging..staging`), the 19 planned plus `13b1b07` (money normalizer deleted), `edc8bcf` (register+schema live-fixes), and the docs `.env.example` slice; order-svc main clean (2 unpushed: `880af5d`, `728e130`); ecom-contracts main clean (1 unpushed: `08e930c`); nothing pushed anywhere |
| G7 | validation script over `tasks.json` (not committed) | **136 tasks, 100 done / 0 in-progress / 36 backlog**, 0 duplicate ids, every `dependsOn` resolves, no cycles, `byRepo` mirrors the entries, sf-051 `done` with a resolving `log` and `verified:true`, no `todo` carries a log or `finished`, sf-054–sf-061 registered with `dependsOn`, `next` recomputed |
| G8 | this file | §0–§6 present; six-storefront-commit hashes listed in §6; the same shape as the consumer-wave report |

---

## 6. Handoff

- **Storefront: 20 commits on `staging`, `268b5d9..edc8bcf`, all local-only.**
  In order: `268b5d9` docs · `8eb25d7` registry+transports · `73f7fed` clients ·
  `43c698b` guest identity+merge · `554d97c` BFF handlers · `04942d4` cart store ·
  `144c75d` stepper+empty-state · `3f53323` gallery+variants · `13b1b07` money
  normalizer deleted · `22dfd8c` mapper+grid · `059d999` hero · `cfb2c94`
  page-header · `ad89900` line-item+drawer+navbar · `c395d03` listing ·
  `60dd174` detail · `8b53286` cart · `eae687c` checkout+confirmation ·
  `339257d` account · `6a02b34` home · `edc8bcf` register two-step + schema.
  (Two extra commits ride the same branch count: the docs `.env` slice and this
  tracker commit's status flip.)
- **The money fix, three other repos, one commit each:** order-svc `880af5d`
  (parse DECIMAL at the DB boundary) + `728e130` (repin 1.10.0), ecom-contracts
  `08e930c` (1.10.0 narrows `refundAmount`; tarball committed, CHANGELOG updated,
  spec flipped to number-only). ADR 41/42 in `DESIGN_DECISIONS.md` carry the
  reasoning; `ec-002`'s follow-up is closed there, not here.
- **Docs moved with the code:** storefront `AGENTS.md` §2/§3 (shop structure, seam
  rules), `Documentation/pages/routing.md` §1 (confirmation route),
  `components/README.md` + `0.Project-Overview.md` index rows (`commerce.md`,
  `sections.md` new; `product.md`, `shell-cart.md` fully done),
  `design-system/storefront.md` path drift fixed, `1.Architecture.md` §6.7 (the
  seam), `.env.example` (three service URLs).
- **What the next agent must NOT re-litigate:** D13's generic 409 (backend change
  is owed, not the regex), D4's client-rendered private routes (the cache rule is
  in `5.Features.md`), D7's context-not-Zustand (revisit only per question 4),
  D20's untouched contracts pin (sf-053 owns it).
- **Open in storefront's queue now:** `sf-052` (track beacon, blocked by
  `anl-002`), `sf-053` (contracts repin — deletes the local response schemas and
  unblocks `sf-060`), then the eight depth tasks registered by this commit.
- **If you inherit this and only read two files:** `lib/http/browser.ts` (the
  whole client-side contract — key minting, single-flight refresh, replay — in
  ~120 lines) and `lib/checkout/idempotency.ts` (the `{key, bodyHash}` model that
  is the reason double-clicking pay is safe). Every island is a consumer of those
  two decisions.
