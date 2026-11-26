# inf-004 — Nginx, VERSIONS.env, per-repo CI and smoke

- Repo: `ecom-infra`
- Phase: P5 · priority: P1 · kind: infra
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `8ff4f01` (config/templates), `17dfdb2` (version registry), `9354f2a` (live edge verification)
- Verified: **2026-11-26 against the live stack**

## What

`nginx/nginx.conf` routes the storefront and each `/api/<service>` prefix;
`VERSIONS.env` pins exact image/library versions; `ci/*.yml` are per-repo
templates that gate on tests; `scripts/smoke-deploy.mjs` probes `/health` and
`/health/ready`.

## Verification (live)

- Pulled public `nginx:stable-alpine`, mounted `nginx/nginx.conf` on the
  compose network with host-gateway aliases, published on port 8080.
- Through the edge: `/health`, `/`, all seven service `/health` and
  `/health/ready` prefixes returned; `/api/catalog/catalog/products` returned
  200 (confirming the prefix rewrite); `/api/cart/cart` and `/api/order/orders`
  returned 401 (auth guard reached). cms/import returned 502 because those
  services were not started — the routing target was reached.
- Earlier in this wave, `/health` and `/health/ready` returned 200 with ready
  bodies for auth, catalog, cart, order, analytics, notify, search and cms.
- `pnpm check:deploy-config` validates the exact pins; `pnpm test:local`
  59/59; all four `check:*` scripts green.

## Caveats

- **Admin routing is intentionally unverified**: `adm-001` was closed as
  deferred at the user's direction, so there is no admin app to route to. The
  acceptance clause is superseded by that decision.
- cms/import containers were not started here, so only routing (502 from the
  configured upstream), not their application responses, was observed.
- CI templates live in `ecom-infra/ci/` as agreed by the repo boundary; they
  are not installed hooks in the service repos. The one CI job that is
  installed and exercised is `.github/workflows/integration.yml` (tst-001).
- A deployed edge smoke against port 80 was not possible; verification used
  the local container on 8080.

## Follow-ups

- Re-run the smoke probe against a deployed edge when one exists.
- Start cms/import if their edge routes need application-level confirmation.
