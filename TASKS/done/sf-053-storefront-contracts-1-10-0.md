# sf-053 — storefront pins contracts 1.10.0 and covers checkout replay (done, 2026-11-01)

## What

The storefront pinned `ecom-contracts-1.7.0.tgz` and validated checkout with two local
schemas. The tracker asked for three things, and one of them could not be met as
written:

1. pin the exact tarball — done, now `1.10.0` (the entry's title still said 1.5.0, which
   was two releases stale);
2. cover success, duplicate key and stock failure — done;
3. "remove the local response schemas" — **not achievable**: contracts ships event
   payloads, not order/cart response DTOs, so `lib/order/schemas.ts` and
   `lib/cart/schemas.ts` are not duplicates of anything the package owns. The
   acceptance line was replaced with "no schema duplicated that contracts now owns".

The audit was recorded rather than assumed: the storefront imports nothing from
`@ecom/contracts` today (three comments mention it, no import), `money` was already
`z.number()` locally and is number-only since 1.10.0, and there is no local
`ctaSchema`/`mediaSchema`/`addressSchema` copy (contracts has no address schema at all).

## How

- `frontend/storefront/package.json`, `pnpm-lock.yaml` — `file:../../ecom-contracts/ecom-contracts-1.10.0.tgz`.
  `@ecom/messaging` stays absent on purpose: the storefront must never gain broker
  credentials.
- `frontend/storefront/test/lib/checkout/replay.test.ts` (new, 197 lines, 5 cases) —
  a stub that mirrors order-svc's replay cache (`key → { hash, confirmation }`):
  - a repeated idempotency key replays the same confirmation and the order is created
    once (both calls carry `attempt-1`);
  - both confirmations pass `checkoutConfirmationSchema`, so a future contract drift
    fails a test instead of the browser — the actual lesson of the 1.5.0 mismatch;
  - `grandTotal: "91.00"` is rejected (money is a number on both sides since 1.10.0);
  - a changed body under the same key answers `409 IDEMPOTENCY_CONFLICT` and still
    creates no second order;
  - a stock failure answers `409` with `STOCK_INSUFFICIENT`, distinct from
    `IDEMPOTENCY_CONFLICT`.
- `next-env.d.ts` — rewritten by `next build` (dev type paths → build type paths) and
  reverted, so the change set is only the manifest, the lockfile and the new test.

## Decisions (+ one rejected alternative each)

1. **Keep `lib/order/schemas.ts` and `lib/cart/schemas.ts`.** They validate responses the
   storefront parses; contracts 1.10.0 exports no such DTO. Rejected: delete them to
   satisfy the original acceptance wording — the client would then trust unvalidated
   JSON.
2. **Do the audit and write it down.** A repin whose only evidence is a green build
   proves nothing about what the package is used for. Rejected: assume the audit,
   because "no imports" is exactly the kind of fact that is wrong once.
3. **Test replay at the client layer with schema-validated fixtures.** Rejected: a
   live-services e2e — the storefront has no harness that boots auth + cart + catalog +
   order, and inventing one is its own task (filed as `sf-053a`).

## Verification

| Check | Result |
|---|---|
| `frontend/storefront` `pnpm test` | 909 passed (117 files), 5 of them new |
| `frontend/storefront` `tsc --noEmit` | exit 0 |
| `frontend/storefront` `next build --webpack` | clean |
| Installed version | `@ecom/contracts 1.7.0 → 1.10.0` |
| commit | `frontend/storefront` `ce15601` |

## Open

- `sf-053a` carries the live checkout harness (P5).
- `checkoutConfirmationSchema` stays storefront-local until contracts exports a response
  DTO; when it does, the local copy should be replaced rather than maintained twice.
