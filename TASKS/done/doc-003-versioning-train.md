# doc-003 — versioning 1.3.0 / 2.0.0 release train

- Repo: `Documentation` (+ `ecom-contracts/VERSIONING.md`)
- Phase: P1 · priority: P0 · kind: docs · transport: docs
- Started: 2026-10-30 · Finished: 2026-10-30

## What

`8.Versioning.md` still described `1.0.0` as the current surface. It claimed
the CMS package "currently ships" the section catalog and ended with "theme,
navigation, pages, blogs, media, page settings, event envelopes, and
`media-resize-image` jobs are added before the first published `1.0.0`" — eight
versions of drift. Rewritten (Version 1.1, 2026-10-30):

| Section | Content |
|---|---|
| §1 | package table, now with `Current version 1.8.0` |
| §2 | tarball distribution; `ecom-infra` pins the local `file:` path, every other consumer the release URL — both exact |
| §3 | **release checklist**, 8 rows, steps 5–6 marked as human approvals |
| §4 | semver rules + queue/topic names: **adding** a registry entry is MINOR, **renaming or removing** one is MAJOR (the name is the contract with the broker) |
| §5 | consumer rules (exact pins, no re-deriving contracts locally, 2.0.0 train) |
| §6 | version history 1.0.0 → 2.0.0 in one table |
| §7 | **the 1.3.0 surface**: per-field table of 1.3.0 status vs 2.0.0 status, plus the five rules of the dual-write window |
| §8 | **the 1.8.0 surface**: every schema family that ships today |
| §9 | **the 2.0.0 train**: five ordered steps with owner and gate |

## The checklist now says what actually went wrong

`1.8.0` is the worked example in §3: adding `src/schemas/queues.ts` also needed a
barrel export in `src/index.ts`, and a missing barrel export passes `tsc` in this
repo and fails only at import time in a consumer. That is why step 3 requires
inspecting the packed tarball and step 5 requires consumer suites before the tag
is approved, rather than promoting `main`.

Steps 5 and 6 are the two a human owns: consumer suites green on the new pin, and
tag approval. Everything else is mechanical.

## Where the train stands

`catalog-svc`, `cms-svc`, `search-svc` and `frontend/storefront` still pin
`1.7.0`, and §3 says so explicitly instead of implying everyone moved: `1.8.0`
only adds schemas none of them import, and `resizeImageJobSchema` is unchanged.
`ec-005` is the task that repins all consumers in one train; `ecom-infra` is the
only 1.8.0 consumer because it is the only thing that reads `TASK_QUEUES` and
`EVENT_TOPICS` at run time.

`ecom-contracts/VERSIONING.md` (shipped inside the tarball) got the matching
one-line rule: adding a queue or topic to a registry is MINOR, renaming or
removing one is MAJOR.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Version history as a table, not one prose section per release | the doc had per-version sections for 1.0.0 and 1.1.0 and nothing after; a table is what stays current | append a §10 every release |
| The 1.3.0 window gets its own section with a field table | it is the one shape every producer writes and the one thing 2.0.0 deletes, so it needs to be readable in isolation | describe it inside the history row |
| §3 is a checklist with commands and artefacts | "run the gates" is not a release process; `pnpm pack` + "the tarball must contain `dist/schemas/*`" is | a numbered prose list |
| 2.0.0 as a five-step train with owners | it is the only change that cannot be rolled out one consumer at a time, so the order *is* the content | a single "remove legacy fields" bullet |

## Open

- The `github.com/E-Commerce-BDA/ecom-contracts` release URL in §2 is the
  documented target, not a published artefact: no tag has been pushed, so all
  local consumers pin `file:` paths (`ec-005` owns the publish).
- §9 step 4 (drain Kafka before removing fields) depends on per-topic retention;
  a 30-day topic means the cutover cannot complete in less than 30 days after
  step 3.
