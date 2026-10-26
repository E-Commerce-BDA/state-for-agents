# ca-004 — Guest merge policies (todo)

## What

Implement `POST /api/v1/cart/merge` for the three policies in
`cart.settings.guestMergeStrategy`: `merge` (default), `guest_wins`, and
`user_wins`, including the never-lose-the-only-cart rule.

## How

- `src/cart/cart-merge.service.ts` — policy selection, deterministic row
  locks, matching-line sum, guest/user conversion, one event.
- `src/cart/cart.repository.ts` — lock both active carts; convert loser;
  reassign guest on `guest_wins`; clear `session_id`.
- `src/cart/cart.controller.ts` — `POST /cart/merge` with JWT +
  `x-session-id` + idempotency key.
- `test/cart-merge.*` — all three policies, only-guest, only-user,
  both-empty, null variant, duplicate lines, retry, one event.

## Decisions

- Default `merge` sums matching lines and appends the rest — least
  surprising for shoppers. Rejected: always guest-wins (loses account
  history).
- `guest_wins` converts the old user cart before reassigning — otherwise
  the partial unique index rejects two active user carts.
- `user_wins` adopts the guest cart when the user cart is empty — never
  discard the only goods. Rejected: literal policy that loses items.
- Defer `ask_customer` — it needs preview + choice UI; adding the enum
  without the flow would be a dead policy.

## Verification

Pending. Gate: unit + e2e green; each policy asserted; retry no-op; one
`cart.updated` after commit; no duplicate line items.
