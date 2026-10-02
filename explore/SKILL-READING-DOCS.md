# SKILL-READING-DOCS — how to read the docs before code

> Scope: every `Documentation/` read. Docs are spec truth; code is checked against them, not the reverse.
> Status: Active | Date: 2026-10-02 | Parent: `SKILL-EXPLORE.md` (orientation)

## Rules

1. **Respect header blocks** (`Scope | Status | Version | Date | Parent`) — stale dates mean verify-against-code before trusting.
2. **`(to create)` rows are tracked gaps, not missing work** — never build an unlisted gap without filing it first.
3. **Doc-vs-code conflict:** trust the newer date, flag it in your summary, never silently follow either. File the reconciliation as a task.
4. **Component docs are read §2-first** (customizable fields table) then §4 (global rules) — §1 (looks) is reference, §3/§5 (scopes/apply-to-all) only when changing admin behavior.
5. **Service docs are read endpoints-first, edge-catalog second** — the catalog, not the happy path, is where production lives.

Use next: router table for your task type.
