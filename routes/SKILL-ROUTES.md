# SKILL-ROUTES — smart shells at the route edge

> Scope: `app/` routes, route groups, root chrome mounting, route islands.
> Applies to storefront-ui (and admin-app when it lands) — never services.
> Status: Active | Date: 2026-10-02 | Parent: storefront `AGENTS.md` §2

## Rules

1. **The route is the smartest file in its tree:** it fetches (via `lib/`), resolves, and passes props. It styles nothing and decides no values — flow is fetch → resolve → vars → props → composed blocks.
2. **State lives in islands:** page-level state in route `_components/` (owned by that route only), shared state in `app/hooks/` (source-injected per `hooks/SKILL-HOOKS.md`). Never in `components/`.
3. **Route groups own chrome:** `(shop)` vs `(auth)` layouts differ; conversion routes render chromeless until their chrome is designed — no placeholder chrome that gets deleted later.
4. **Root chrome mounts once:** shell (navbar/drawers/overlays) mounts at root layout; pages inherit it. Per-page overrides travel as settings, never as conditional markup in the shell.
5. **`?next=` / `?token=` handling belongs to the page:** internal-path guard on `next` (open-redirect rule), token presence selects the reset step. Both validated server-side, displayed client-side.

Use next: `hooks/SKILL-HOOKS.md` (stateful composition), `lib/SKILL-FUNCTIONS.md` (resolvers).
