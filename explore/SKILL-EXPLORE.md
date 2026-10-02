# SKILL-EXPLORE — how to explore the project

> Scope: mandatory first skill for any task. Never assume paths.
> Status: Active | Date: 2026-09-30

## Rules

1. Start at `state-for-agents/SERVICES.md` + `STATUS.md` (or `tasks.json`) — find the row + owner doc for your task.
2. Then `glob` for filenames, `grep` for symbols (event names, component names, error codes); `read` the owner doc section before code.
3. Respect header blocks (`Scope | Status | Parent`) and `(to create)` rows — gaps are tracked, not missing.
4. Path truth: repos `storefront-ui/`, `admin-app/`, per-service repos (not `frontend/*` — rewrite old refs); specs in `Documentation/`, status in `state-for-agents/`.
5. If doc and code disagree, trust the newer date, flag it in your summary, don't silently follow either.

Use next: SKILL-ROUTER table for your task type.
