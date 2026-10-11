# sf-030 — Customization skill + Button fill (done 2026-10-11)

Skill for agents to answer "what can admin change on X?" from the matrix.
First progressive fill: Button (one component per turn cadence).

## Commits (state-for-agents unless noted)
1. Tracking open. 2. ui/SKILL-CUSTOMIZE.md. 3. Router lane.
4. Matrix Button rows (Documentation). 5+. Verify + close.

## Locked answers (user)
- Per build task, one component per turn. Markdown only (no JSON mirror).

## Verification

Skill self-test passed: 4 probe questions (Button variants, palette
width, Toast knobs, cadence rule) all answered strictly from the matrix.
Router lane present. Zero code touched (storefront clean) — suite
untouched by construction. 3 tracking commits + 1 doc commit, local.

## Follow_ups

- Next fills, one per turn: Input, IconButton, Dialog, Card (then sections).
- state-for-agents still unpushed (push is the human's call).
