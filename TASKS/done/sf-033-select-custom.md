# sf-033 — Select custom dropdown (done 2026-10-11)

Native prop extension + custom listbox branch + theme.select group.
Native list-interior knobs documented-ignored (OS chrome law).

## Locked answers (user)
- Full WAI listbox keyboard. Arrow = CMS media URL (glyph fallback).

## Order (one commit per file)
1. Tracking. 2. Native props. 3. Listbox branch. 4. CSS + guard.
5. Theme + resolver. 6. Trio. 7. Matrix + admin. 8. Gate + close.

## Verification

`tsc` clean; suite 249/249 (14 new); `next build` green. Gate caught
TWO real bugs: orphaned palette guard (animation dead since sf-023,
stray brace — repaired, arrival plays now) + translateY(-50%) vs
wave-park (restructured). AGENTS allowlist carries the select-popup
exemption with reason. ~12 code commits + 2 doc commits, local.

## Follow_ups

- Assembler/showcase pass theme.select into Select (wiring, not new API).
- Per-option disabled states (needs SelectOption.disabled + skip logic).
