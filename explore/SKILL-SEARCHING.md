# SKILL-SEARCHING — how to search the codebase

> Scope: locating code across all repos before touching anything. Mandatory
> before any edit outside files already read this session.
> Status: Active | Date: 2026-10-02 | Parent: `SKILL-EXPLORE.md` (orientation)

## Rules

1. **Filenames first (`glob`), symbols second (`grep`), reading last (`read`).** Never `read` a path you haven't confirmed exists — guessing paths wastes the most expensive resource (context).
2. **Trace events end to end:** producer (`publish(`) → envelope type → every consumer (`subscribe(`). A change touching one end without the other is incomplete by definition.
3. **Trace error codes the same way:** code string → emitter (service/guard) → display map (`lib/auth/errors.ts` style) → rendered copy. Display text is never edited at the render site.
4. **Trace vars upward:** a CSS `var(--x-*)` → inline `style` emitter → resolver → CMS key. Paint bugs are fixed where the value is decided, never where it renders.
5. **Path truth:** repos are `storefront-ui/`, `admin-app/`, per-service repos — never `frontend/*` (rewrite old refs on sight). Specs in `Documentation/`, status in `state-for-agents/`.

Use next: `SKILL-READING-DOCS.md` (doc sections before code), router table for your task type.
