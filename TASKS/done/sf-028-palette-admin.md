# sf-028 — Palette admin expansion (done 2026-10-11)

Footer flush-harden + full admin knobs (geometry, visibility, rowAction,
pillRadius, notify) + Toast primitive + customization matrix doc.

## Locked answers (user)
- View button semantics: onView callback (lands with view task, not stubbed).
- Notify default: on.

## Order (one commit per file)
A. Footer flex-column harden. B. PaletteField expansion. C. Resolver.
D. Component + CSS. E. Toast slice. F. Tests. G. Matrix doc.
H. Showcase notify. I. Gate + close.

## Verification

`tsc` clean throughout; suite 222/222 (10 new: toast 5, gates/vars/units;
literal-drift fixed visibly); `next build` green. Footer double-pinned.
~17 code commits + 3 doc commits, local, unpushed.

## Follow_ups

- `notifyOnQuickAdd` consumed by the assembler (sf-026), not the palette —
  showcase demos default-on. View task brings onView + view/both branches.
- Hard-refresh §17: prior screenshot gap matched pre-sf-027 geometry.
- Stray lab HTML still untracked (user's file).
