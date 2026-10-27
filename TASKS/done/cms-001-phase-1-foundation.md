# cms-001 — Phase 1 foundation for cms-svc

## What

Built the `cms-svc` Phase 1 foundation so later CMS domain work starts from a
verified service instead of a blank Nest scaffold. The service now boots with
validated configuration, connects to MongoDB with fail-fast behavior, treats
Redis as a degraded dependency, exposes liveness/readiness probes, and carries
shared request-id, error-envelope, cache-control, JWT, and role-guard plumbing.
No CMS collections, domain endpoints, Zod contracts, events, S3/media, or app
Dockerfile were added.

## How

- `src/app.module.ts`, `src/app.setup.ts`, `src/main.ts` — global config,
  shared HTTP setup, `/api/v1` prefix with health excluded, ESM bootstrap.
- `src/config/env.validation.ts` — Joi schema for `NODE_ENV`, `PORT`,
  `MONGODB_URI`, `JWT_SECRET`, `REDIS_URL`.
- `src/db/db.module.ts` — global Mongoose connection with 5s selection and
  fail-fast startup.
- `src/redis/redis.service.ts`, `src/redis/redis.module.ts` — single ioredis
  client, offline queue disabled, shutdown cleanup.
- `src/health/*` — liveness and readiness; Mongo critical, Redis degraded.
- `src/auth/*` — JWT module, `JwtAuthGuard`, `RolesGuard`, `@Roles()`.
- `src/common/*` — request-id middleware, exception filter, cache-control
  interceptor.
- `test/*`, `src/**/*.spec.ts` — unit and e2e coverage against real Mongo and
  Redis.
- `docker-compose.yml`, `.env.example`, `README.md` — local runbook.

## Decisions (+ one rejected alternative each)

1. **Dockerized Mongo on `127.0.0.1:27018`.** Keeps the CMS isolated from the
   native Mongo on `27017`, makes reset/delete safe, and leaves Atlas for the
   separate Phase 7 staging smoke. Rejected: using the native Mongo instance,
   because test data and local dev data would share an unmanaged server.
2. **Fail-fast Mongo, degraded Redis.** Mongo is the content source of truth;
   starting without it would serve empty content. Redis only accelerates reads,
   so readiness reports it as `down` while still returning `200` when Mongo is
   healthy. Rejected: making Redis critical, because a cache outage would take
   the CMS down for no correctness reason.
3. **JWT verification pinned to `HS256`, issuer `ecom-auth`, audience
   `ecom-api`, 30s clock tolerance.** Matches the platform auth contract and
   prevents accepting tokens minted for another service. Rejected: decoding
   without issuer/audience checks, because that accepts tokens from any peer
   sharing the secret.
4. **Shared `configureApp` for production and e2e tests.** Prevents global
   behavior from drifting between the real bootstrap and tests. Rejected:
   duplicating setup in `main.ts` and each test, because the two paths would
   eventually diverge.
5. **Type-only Mongoose `Connection` import.** Decorator metadata kept the
   type as a runtime import, which broke `node dist/main.js` because Mongoose
   has no named `Connection` export. Rejected: switching the whole service to
   CommonJS, because the ESM build is intentional and the import was the actual
   defect.

## Verification

- `pnpm lint`: 0 warnings / 0 errors.
- `pnpm test`: 35 tests across 7 files passed.
- `pnpm test:e2e`: 5 tests across 2 files passed against real Mongo + Redis.
- `pnpm typecheck`: clean.
- `pnpm build`: clean, includes `dist/main.js`.
- Production smoke: `/health` `200`, `/health/ready` `200` with both
  dependencies up, unknown API route `404` with the standard envelope.
- Mongo-down smoke: `/health/ready` `503` with `mongo: "down"`, `redis: "up"`.
- Commit: `cms-svc` `ad792c3` (`feat: add phase 1 foundation`).
