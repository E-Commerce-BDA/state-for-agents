# inf-001 — one compose file for the whole local stack

- Repo: `ecom-infra` (+ `cms-svc` env, `Documentation`)
- Phase: P1 · priority: P0 · kind: infra · transport: infra
- Started: 2026-10-30 · Finished: 2026-10-30

## What

There was no single local stack. Four dependency containers had been started
three different ways:

| Container | Owner before | Provenance |
|---|---|---|
| `ecom-pg` | `auth-svc/docker-compose.yml` | compose project `auth-svc` |
| `ecom-cms-mongo` | `cms-svc/docker-compose.yml` | compose project `cms-svc` |
| `ecom-kafka` | `docker-compose.kafka.yml` at the repo root | compose project `e-commerce` |
| `ecom-redis` | nobody | `docker run`, no compose labels, anonymous volume |

`docker compose ls --all` identified the three projects; `ecom-redis` had no
labels at all, so it could never be reproduced from the repository. The single
file is `ecom-infra/docker-compose.yml` with `name: e-commerce`, seven services
(postgres, redis, mongo, mongo-rs-init, kafka, localstack, mailpit), fixed
network `ecom-net`, and five named volumes.

## Data migration

The Postgres volume was the only volume carrying work that cannot be recreated.

1. Census before: `auth 7/486, cart 6/5, catalog 17/376, order 8/976, search 2/12`
   = 40 tables / 1855 rows.
2. `pg_dump -Fc` for `ecom` and `ecom_search_test` inside `ecom-pg`, copied out
   with `docker cp` to `ecom-infra/.tmp/`.
3. `docker rm -f ecom-pg ecom-redis ecom-kafka ecom-cms-mongo`.
4. `docker compose -f ecom-infra/docker-compose.yml up -d`.
5. `pg_restore --no-owner --no-privileges --exit-on-error` into the fresh
   container, then `CREATE DATABASE ecom_search_test` and restore it.
6. Census after: identical — `Compare-Object` between the two census files
   returned nothing.

Mongo was **not** migrated: the only database in `ecom-cms-mongo` was
`ecom_cms_test`, and every cms e2e suite calls `connection.dropDatabase()` on it,
so the data was disposable by definition.

## Mongo had to become a replica set

`cms_outbox` needs a transaction and a standalone `mongod` cannot start a
session, so `ecom-mongo` runs `--replSet rs0` and a one-shot `mongo-rs-init`
container runs `rs.initiate` (`[rs-init] rs0 has a writable primary`). The health
check is `isWritablePrimary`, not "the process is alive", so a healthy container
is one that can accept a transaction.

The cost is that the member advertises itself as `mongo:27017`, a name that only
resolves inside `ecom-net`. Proved with a mongoose probe: a plain
`mongodb://127.0.0.1:27018/ecom_cms` fails with
`MongooseServerSelectionError: getaddrinfo ENOTFOUND mongo`, while adding
`?directConnection=true` runs a transaction that aborts cleanly. `cms-svc/.env`,
`cms-svc/.env.example` and `cms-svc/test/setup-env.ts` now carry the parameter
with a comment; the cms suite is 75/75 green afterwards.

## Container removal

Removed after the new stack was verified, in this order: the three retired
compose files (`docker-compose.kafka.yml`, `auth-svc/docker-compose.yml`,
`cms-svc/docker-compose.yml`), the four containers, then the five legacy volumes
(`auth-svc_ecom-pgdata`, `cms-svc_ecom-cms-mongo-data`, `e-commerce_ecom-kafka-data`
and the two anonymous volumes). The surviving volumes are all `e-commerce_*`.

`cms-svc` `db:up`/`db:down` now point at `../ecom-infra/docker-compose.yml` so the
service keeps a one-command database without its own compose file.

## Verification

`node scripts/verify-stack.mjs` → **31/31**: six containers healthy,
`mongo-rs-init` exited 0, one compose project, Postgres schema floors
(`auth 7, cart 6, catalog 17, order 8, search 2`) plus `ecom_search_test`, a Mongo
transaction, three SQS queues + three DLQs (`maxReceiveCount 5`, `waitTime 20`,
`retention 1209600`), and one SMTP message stored by Mailpit.

Four defects in the verifier itself were found and fixed on the way:

1. `select table_schema || '=' || count(*) … group by 1` is invalid Postgres →
   select two columns.
2. `compose ps --format json` omits exited containers, so the one-shot init
   container looked missing → `--all`.
3. LocalStack returns `maxReceiveCount` as a number, not a string → compare
   `String(...)`.
4. The raw-socket SMTP probe never settled; replaced by a real
   `docker exec -i ecom-mailpit /mailpit sendmail …` plus an HTTP read of 8025.
   (`--to` is not a mailpit flag — recipients are positional.)

## Open

- `pgdata` is the one volume that is not disposable; a full reset
  (`docker compose down -v`) empties every service database.
- The six service repos still document `ecom-cms-mongo` in a few places; the
  container is `ecom-mongo` now (`ecom-infra/README.md` and
  `Documentation/services/cms.md` were updated).
