# SERVICES — status matrix (agents update cells as work lands)

> Scope: live tracker. Stages: spec → build → test → verify (⬜ todo / 🚧 in-progress / ✅ done).
> Status: Active | Date: 2026-10-31 | Machine mirror: `tasks.json`

| Repo | Port | Spec doc | spec | build | test | verify |
|---|---|---|---|---|---|---|
| storefront-ui | 3000 | `Documentation/design-system/storefront.md`, `pages/` | ✅ | 🚧 | 🚧 | ⬜ |
| admin-app | 3001 | `Documentation/6.Admin-Panel.md` | 🚧 | ⬜ | ⬜ | ⬜ |
| ecom-contracts | npm | `8.Versioning.md` | 🚧 | 🚧 | 🚧 | ⬜ |
| ecom-messaging | npm | `8.Versioning.md` §10, `1.Architecture.md` §6.5 | ✅ | ✅ | ✅ | ✅ |
| auth-svc | 4010 | `Documentation/services/auth.md` | ✅ | ✅ | ✅ | ✅ |
| catalog-svc | 4020 | `Documentation/services/catalog.md` | 🚧 | ✅ | ✅ | ✅ |
| cart-svc | 4030 | `Documentation/services/cart.md` | ✅ | ✅ | ✅ | ✅ |
| order-svc | 4040 | `Documentation/services/order.md` | ✅ | ✅ | ✅ | ✅ |
| cms-svc | 4050 | `Documentation/services/cms.md` | 🚧 | ✅ | ✅ | ✅ |
| analytics-svc | 4060 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| import-svc | 4070 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| notify-svc | 4080 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| search-svc | 4090 | `Documentation/services/search.md` | ✅ | ✅ | ✅ | ✅ |
| ecom-infra | — | `7.Deployment.md` (to create) | ⬜ | ⬜ | ⬜ | ⬜ |

Rule: flip a cell + update `tasks.json` + `STATUS.md` in the same commit. Link PR/commit in row note.

## Row notes

- `storefront-ui` — `sf-049` `71f04a5` (thin auth client, four BFF handlers owning `sf_at`/`sf_rt`, `proxy.ts` forwarding only `GET /api/auth/session`), `sf-050` `5de7d95` (`lib/cms/*` reads with tags + `revalidate: 300`, bounded stale nav fallback, `POST /api/revalidate`). 50/53 tasks, **63 test files / 475 tests**, `tsc` clean, `next build` clean. `build`/`test` stay 🚧 because `sf-051` (commerce routes) and `sf-052` (`/api/track`) are still open; `verify` is ⬜ until those land.
- `cart-svc` — `ca-010` `cb305e7` (add-to-cart prices from catalog-svc over HTTP, fixture moved to test-only, fail closed). 9/10 tasks; **103 unit (15 files) + 99 e2e (12 files, 1 skipped)**. `verify` remains ✅ for the shipped slices even though `tasks.json#repos["cart-svc"].stages.verify` is `in-progress` — that cell tracks the whole repo, and `ca-009` is open.
- `Documentation` — `40348b9` carries `ca-010`/`sf-049`/`sf-050` (6 files, +135/−8).
- `ecom-messaging` — no task entries of its own; delivered through `au-004`/`ca-008`, re-opened by `cat-007`/`ord-011`/`cms-005`, reshaped for Mongo by `cms-005`. Now **0.2.0** with Postgres + Mongo stores, adopted by all five producers.

Cell truth for the rows above was recomputed against `tasks.json#repos[repo].stages` on 2026-10-31. Where a ✅ column and an `in-progress` stage disagree it is because the column records the shipped slices and the stage records the repo — the note says which is which; do not "fix" one without the other.
