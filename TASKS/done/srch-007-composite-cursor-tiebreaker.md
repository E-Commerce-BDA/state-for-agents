# srch-007 — make the search cursor a total order across document types (done, 2026-11-24)

- Repos: `search-svc`
- Phase: P0 | priority: P0 | kind: bug | transport: http
- Started: 2026-11-24 | Finished: 2026-11-24

## What

`srch-004` made the primary key `(document_type, id)`, but `CursorPayload` still
used `id` as its only tie-breaker. Every keyset predicate and `ORDER BY` in
`search.repository.ts` ended at `id`, so a product and a category sharing an id
at equal sort keys were not totally ordered: a page walk could skip or repeat
rows. That is the same defect class the catalog cursor had in `cat-015`.

The cursor now carries a required `document_type` and is version 2. All five
sorts order by `document_type` before `id`; each predicate closes with
`(document_type < $t OR (document_type = $t AND id < $id))`, with `>` for
`price.asc`. The service writes the type from the last row. Version 1 cursors
are rejected with `CURSOR_INVALID`.

## Why

A composite key needs a composite tie-breaker. A bare id cannot order two
documents of different types that happen to share one, and no amount of query
fingerprinting fixes that — the fingerprint already contains the `type` filter
and an unfiltered query still has the collision.

Rejected: keeping an optional type on v1, because old cursors would decode and
return subtly wrong pages that no test or dashboard would flag. Rejected:
dual-reading both formats; a loud 400 and a restarted walk is the honest
failure mode for a short-lived pagination token.

## How

- `cursor.codec.ts`: required `type`, `v: 2`, explicit v1 rejection and type
  validation; all fixtures updated.
- `search.repository.ts`: `document_type` added to every `ORDER BY` and every
  keyset predicate, with direction matching the sort.
- `search.service.ts`: emits `type: last.document_type`.
- New `test/search.cursor-predicate.spec.ts` inspects the generated SQL and
  parameters through a mocked pool, so the ordering rule is checked without a
  live database.
- Commit `b4c9d13` in `search-svc`.

## Verification

- `npx tsc --noEmit` exit 0.
- `pnpm test`: 21 files / 150 tests passed (up from 20 / 142).
- `pnpm lint` and `pnpm build` exit 0; one pre-existing unused-variable warning
  in the untouched `src/indexer/event-mapper.ts`.
- `pnpm test:e2e` cannot run here: the test Postgres is unavailable and
  requests return 503. Not claimed as green.

## Follow-ups

- Clients holding a v1 cursor receive a 400 and must restart pagination.
- The SQL-level predicate spec is a unit test; a live walk over a seeded
  shared-id pair still needs the test database.
