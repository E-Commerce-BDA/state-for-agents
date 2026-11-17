# cat-015 — catalog keyset cursor and derived listing facets (done, 2026-11-17)

## What

The public product list had a broken cursor: `nextCursor` was a bare product id
and the walk used `p.id > $cursor` against `ORDER BY created_at DESC, id DESC`,
which repeats rows (measured 78 repeats on page 2 of 100). This task replaced it
with a proper keyset walk and added a facets endpoint for the storefront filter
rail.

## How

- `src/products/cursor.codec.ts`: opaque base64url payload `{v, q, sort, id,
  createdAt?, price?, name?, rating?, popularity?, orderIndex?}`. The fingerprint
  is SHA-256 over every membership-affecting filter plus the effective sort;
  decode rejects a wrong version, a mismatched fingerprint, a mismatched sort or
  a malformed id with `CURSOR_INVALID` (400 via the service layer).
- `findList` decodes once, then adds a composite predicate on the *same* columns
  the `ORDER BY` uses (`(created_at, id)`, `(price, id)`, `(name, id)`,
  `(popularity, id)`, NULL-last rating, manual `array_position`). `nextCursor`
  is encoded from the last row's sort key.
- `GET /products/facets?categoryId=&brandId=` returns distinct tags and price
  bounds from active rows (`DISTINCT unnest(tags)`, `min/max(price)`), never a
  seeded list.
- Tests: codec unit (round-trip, mismatch, malformed); e2e asserts no duplicate
  ids across pages, a malformed cursor is refused, and facets are derived.

## Decisions (+ one rejected alternative each)

1. **Opaque keyset cursor over a bare id** — the old predicate was not on the
   ordering columns, so pages overlapped. Rejected: patching the old predicate
   with an offset, which drifts under inserts.
2. **Fingerprint the filters** — a cursor from another filter set must not
   silently change the result. Rejected: trusting the client to pair a cursor
   with the right filters.
3. **Facets derived from rows** — a tag the rail offers is a tag a real product
   carries. Rejected: a hardcoded tag list or deriving from one 100-row page.

## Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | green |
| `pnpm test` | 165 tests / 25 files green |
| e2e (`products.e2e-spec.ts`) | added, not run — local Postgres down in this session |
