# adm-001 — admin app: scope decision (deferred)

- Repo: `admin-app` (not created)
- Phase: P6 · priority: P2 · kind: feature
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): none — no repo scaffolded

## What

The scope decision is **deferred**, at the user's direction, while the remaining
backend and integration work is finished. The task's own acceptance criteria
allow this path: "If deferred: STATUS and tasks.json say so explicitly."

No `admin-app` repository, Next 16 scaffold, auth guard, or merchant screens
were created. No Kafka or SQS client was added anywhere.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Defer the admin app | Backend acceptance is API/curl-based, and the remaining 12 backlog items are integration and live-stack verification; building a second frontend now would rework it after backend changes | Scaffold products/orders/CMS/theme screens now |
| Do not create the repo yet | An empty repo would add a 16th push target with no code and no owner | Placeholder scaffold |

## Verification

- `tasks.json` records this task as done with `verified: true` and the decision
  in `follow_ups`; `STATUS.md` states the deferral explicitly.
- Confirmed no `E:\E-Commerce\admin-app` directory and no admin CI target with
  code behind it (`ecom-infra/ci/admin-app.yml` is an unused template).

## Follow-ups

- Reopen when merchant UI is required for acceptance. If it is, start with
  products, orders, CMS sections and theme settings, and keep the app on HTTP
  seams only — no direct Kafka or SQS client.
