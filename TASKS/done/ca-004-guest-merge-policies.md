# ca-004 — Guest merge policies (done, 2026-10-27)

## What

Implemented `POST /api/v1/cart/merge` for the three policies in
`cart.settings.guestMergeStrategy`: `merge` (default), `guest_wins`, and
`user_wins`, including the never-lose-the-only-cart rule.

## How

- `src/cart/cart-merge.service.ts` — reads the effective policy, delegates
  the locked transaction, returns `{cart}`, and emits one `cart.updated`
  after commit only when a guest cart was consumed.
- `src/cart/cart.repository.ts` — locks the active user and guest carts in
  id order, adopts only a non-empty guest cart, sums matching
  `(product_id, variant_id)` lines with user snapshots winning, appends
  guest-only lines, converts losers, clears the adopted guest `session_id`,
  and retries one unique-conflict race.
- `src/cart/cart.controller.ts` — `POST /cart/merge` requires a verified
  user, `x-session-id`, and the idempotency interceptor's
  `x-idempotency-key`.
- `src/auth/guards/cart-identity.guard.ts` — carries `guestSessionId`
  alongside a verified user identity without changing guest-only routes.
- `src/cart/cart.mapper.ts` — shared DTO, totals, and `cart.updated`
  construction for CRUD and merge.
- `src/settings/settings.service.ts` — `getGuestMergeStrategy()` reads the
  versioned setting at merge time.
- `test/cart-merge.e2e-spec.ts` — all three policies, only-guest,
  only-user, both-empty, null variant, matching/guest-only lines, converted
  history, retry no-op, one event, and missing key/session/token.

## Decisions

- Default `merge` sums matching lines and appends the rest — least
  surprising for shoppers. Rejected: always guest-wins (loses account
  history).
- `guest_wins` converts the old user cart before reassigning — otherwise
  the partial unique index rejects two active user carts.
- `user_wins` adopts the guest cart when the user cart is empty — never
  discard the only goods. Rejected: literal policy that loses items.
- A guest cart is adopted only when it has items. This gives `merge` and
  `user_wins` the same never-lose rule and keeps `guest_wins` from
  replacing a useful user cart with an empty guest cart.
- Merge returns `{cart}` only, matching the API contract. The client can
  `GET /cart` for items/totals.
- E2E overrides `SettingsService` with a controllable policy selector so
  merge tests do not race the global settings E2E.
- Defer `ask_customer` — it needs preview + choice UI; adding the enum
  without the flow would be a dead policy.

## Verification

- `pnpm test`: 79 passed / 12 files (merge service + guard + settings
  additions).
- `pnpm test:e2e`: 58 passed / 6 files; merge matrix is 12 tests.
- `pnpm exec tsc --noEmit`: clean.
- `pnpm lint`: 0 errors / 0 warnings.
- `pnpm build`: clean.
- Local cleanup: 0 carts, 0 cart items, 0 settings audit rows; settings
  `global` / `{}` / version `0`; 0 Redis `idem:*` keys.

## Code commits

`f876b1d` mapper · `e9e6d0f` service mapper use · `e1df339` mapper test
import · `2a4ace4` guard guest session · `eeadff7` guard test · `89aa192`
settings read · `bc6f19f` settings test · `5b3aa0f` merge response type ·
`66f6427` repository merge · `d5dd2a7` merge service · `257e2c5` controller
route · `99e24db` module wiring · `873008b` merge service test · `7d3eda4`
merge E2E.

## Follow-ups

- Commit the existing uncommitted `cart-svc/src/app.module.ts`
  (`CartModule` import + `JWT_SECRET` validation). The working tree is
  wired, but the cart-svc commit chain does not import `CartModule` until
  that file is committed.
- Lock/verify the active cart status inside item mutations. A concurrent
  add can currently pass `ensureActiveCart` before a merge converts that
  cart, then insert into the converted cart after the merge commits.
- Consider returning the merged items from the transaction (or building
  the event there) so a post-commit `findItems` failure cannot turn a
  committed merge into a 500.
- Replace `NoopEventBus` with Kafka/outbox; add `HttpCatalogClient`,
  Redis readiness, rate limits, and the append-only least-privilege
  settings-audit role.
