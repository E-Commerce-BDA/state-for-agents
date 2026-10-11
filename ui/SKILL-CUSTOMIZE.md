# SKILL-CUSTOMIZE — answer "what can admin change on X?"

> Scope: reading `Documentation/components/customization.md` (the only knob inventory) + authoring new knobs correctly.
> Status: Active | Date: 2026-10-11 | Parent: `SKILL-DUMB` (leaves) + `SKILL-INTERFACES` (shapes)

## Rules

1. **Read the matrix first.** `Documentation/components/customization.md` is the only source — never a JSON mirror beside it (mirrors rot; markdown serves humans and agents). States legend: **live** = works end-to-end, **settings-only** = vocabulary resolved without a component, **stub** = one-liner filled by its slice.
2. **Knob conventions:** admin fields sparse-optional (absent = inherit, never `null`); resolved types all-required; literals live only in `DEFAULT_*`; numerics clamp in the resolver; garbage strings clean to builtins; v1-only unions extend, never loosen.
3. **Pipeline map:** settings → resolver → theme/vars → component. Components never import CMS; owners own timing and notifications (Toast rule: `notifyOnQuickAdd` gates the owner's effect, not the primitive).
4. **Progressive rule:** one component's rows per build turn, same-commit with its knobs. No knob without a row; no row without a knob. A slice that adds settings but skips the matrix isn't done.
5. **If the matrix lacks the surface**, the surface's doc (`pill.md`-shape) is also missing — file the doc first, then the rows. Never invent knob names from code alone; the matrix is the vocabulary contract.

```md
// GOOD — question answered from the matrix, knob cited with type+default
"Palette card width? `cardMaxWidth`, clamped px 480–960, default 720
 (customization.md → Search overlays → Palette)."
// BAD — invented from code, bypassing the contract
"The card takes a `width` prop, probably pixels."
```

Use next: `lib/SKILL-INTERFACES.md` (shapes), `ui/SKILL-DUMB.md` (leaves), `ui/SKILL-CSS.md` (paint), `project/SKILL-SEO.md` (headings/links).
