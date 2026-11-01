# cat-011 — the fixture seed runs only behind an explicit flag (done, 2026-11-01)

## What

`db/002-seed-catalog.sql` writes a demo catalogue, and the only documented way to run
it was `psql -f db/002-seed-catalog.sql` against whatever `DATABASE_URL` happened to
point at. That is one copy-paste away from loading fake products into a real shop, and
nothing in the service noticed.

cat-011 puts two guards on it: the script refuses unless `NODE_ENV` is not `production`
**and** `CATALOG_ALLOW_FIXTURE_SEED=true`, and the service refuses to boot when the flag
is on in production. Production data arrives through the admin CRUD routes and through
`product.imported`.

## How

- `catalog-svc/src/config/fixture-seed.guard.ts` (new) — `assertFixtureSeedAllowed(env)`
  throws when `NODE_ENV === 'production'` and `CATALOG_ALLOW_FIXTURE_SEED === 'true'`.
  Takes `env` as a parameter so the spec needs no `process.env` mutation.
- `catalog-svc/src/main.ts` — the guard runs before `NestFactory.create`, so a
  misconfigured box never opens a database connection.
- `catalog-svc/db/seed.mjs` (new) — refuses with a one-line reason and exit 1 when
  `NODE_ENV=production` or the flag is not `true`; otherwise reads
  `002-seed-catalog.sql`, runs it through `pg` (no `psql` on the host) and prints the
  row count of every table it wrote, in dependency order.
- `catalog-svc/package.json` — `"db:seed": "node db/seed.mjs"`.
- `catalog-svc/.env.example` — `CATALOG_ALLOW_FIXTURE_SEED=false`, with the two real
  paths named in the comment.
- `catalog-svc/src/config/fixture-seed.guard.spec.ts` (new, 4 cases) — throws in
  production with the flag, allows development with the flag, allows production when
  the flag is absent or false.
- `catalog-svc/README.md` §Database — the manual `psql` block replaced by
  `pnpm db:seed` plus the refusal rule; `Documentation/services/catalog.md` gained the
  same sentence.
- `ecom-infra/docker-compose.yml` — checked, not changed: nothing invokes the seed.

## Decisions (+ one rejected alternative each)

1. **Two guards, not one.** The script guard covers an operator running a command; the
   bootstrap guard covers a deployed process whose compose file sets the flag by
   accident. Rejected: guard only in the script, which leaves a running service that
   serves demo data happily.
2. **Guard the flag, not the file name.** `CATALOG_ALLOW_FIXTURE_SEED` is a deliberate
   act; a path check would let any copy of the SQL through under another name.
   Rejected: refuse only when the SQL file is named `002-seed-catalog.sql`.
3. **Run the SQL through `pg` from `db/seed.mjs`.** The host has no `psql`, and a script
   can report what it inserted. Rejected: keep the documented `psql -f` one-liner and
   guard nothing.
4. **No compose change.** Nothing in `ecom-infra` calls the seed, so adding a
   `SEED=1` profile would create a second way in. Rejected: a seed sidecar in compose.

## Verification

| Check | Result |
|---|---|
| `catalog-svc` `pnpm test` | 157 passed (24 files) |
| `catalog-svc` `fixture-seed.guard.spec.ts` | 4 cases: production + flag throws, development + flag allowed, production without the flag allowed, production with `false` allowed |
| `catalog-svc` `pnpm db:seed` (development, flag on) | applies the SQL and prints one row count per table |
| `catalog-svc` `pnpm db:seed` (flag off) | exits 1 with `catalog fixture seed refused: …` before opening a connection |
| `catalog-svc` `pnpm lint` | 0 warnings, 0 errors (133 files) |
| `catalog-svc` `nest build` | clean |
| commit | `catalog-svc` `3916f9c` |
