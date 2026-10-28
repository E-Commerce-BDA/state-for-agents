# SERVICES — status matrix (agents update cells as work lands)

> Scope: live tracker. Stages: spec → build → test → verify (⬜ todo / 🚧 in-progress / ✅ done).
> Status: Active | Date: 2026-10-28 | Machine mirror: `tasks.json`

| Repo | Port | Spec doc | spec | build | test | verify |
|---|---|---|---|---|---|---|
| storefront-ui | 3000 | `Documentation/design-system/storefront.md`, `pages/` | 🚧 | ⬜ | ⬜ | ⬜ |
| admin-app | 3001 | `Documentation/6.Admin-Panel.md` | 🚧 | ⬜ | ⬜ | ⬜ |
| ecom-contracts | npm | `8.Versioning.md` | 🚧 | 🚧 | 🚧 | ⬜ |
| auth-svc | 4010 | `Documentation/services/auth.md` | ✅ | ✅ | ✅ | ✅ |
| catalog-svc | 4020 | `Documentation/services/catalog.md` | 🚧 | 🚧 | 🚧 | ⬜ |
| cart-svc | 4030 | `Documentation/services/cart.md` | ✅ | ✅ | ✅ | ✅ |
| order-svc | 4040 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| cms-svc | 4050 | `Documentation/services/cms.md` | in-progress | in-progress | in-progress | todo |
| analytics-svc | 4060 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| import-svc | 4070 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| notify-svc | 4080 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| search-svc | 4090 | (to create) | ⬜ | ⬜ | ⬜ | ⬜ |
| ecom-infra | — | `7.Deployment.md` (to create) | ⬜ | ⬜ | ⬜ | ⬜ |

Rule: flip a cell + update `tasks.json` + `STATUS.md` in the same commit. Link PR/commit in row note.
