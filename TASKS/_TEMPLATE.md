# TASKS/<status>/<repo>-<NNN>-<slug>.md — log template

> Filename == entry id. Folder == entry status. Move the file on stage
> change; update the entry + STATUS.md + summary in the same commit.

## What

One paragraph: what was built/changed and why it was needed.

## How

Files touched (paths), in dependency order. Key implementation notes
(≤5 bullets). No full code — the repo holds code; the log holds reasons.

## Decisions (+ one rejected alternative each)

Each design decision with its reason. Learning rule: answers without
reasons are incomplete.

## Verification

Test counts, `tsc`, build results, commit hashes. Green numbers only —
red goes back to in-progress, never to done.
