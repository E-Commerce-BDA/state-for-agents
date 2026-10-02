# SKILL-VERCEL — separate deployments for the two UIs

> Scope: `storefront-ui` + `admin-app` as two Vercel projects. Services stay on EC2.
> Status: Active | Date: 2026-09-30

## Rules

1. Two Vercel projects, roots `storefront-ui/` and `admin-app/`; framework Next.js; build `next build`; Node 20+.
2. Env per project (never shared): API base (`https://api.example.com`), `TRANSPORT` irrelevant for UI reads except `/api/track` forward, CMS preview secret for `?preview=1`.
3. Preview deploys per PR; production only from `main`; env + preview secret via Vercel dashboard (never git).
4. Anything stateful (Postgres/RDS, Mongo, Redis, Kafka/SQS workers, Nginx) stays out of Vercel — Vercel serves UI + ISR only.

Use next: SKILL-FRONTEND, SKILL-SEO.
