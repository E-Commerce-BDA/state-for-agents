# ec-005 — contracts release train: tags and GitHub Releases

- Repos: `ecom-contracts`, `ecom-messaging` (+ all 15 pushed repos)
- Phase: P5 · priority: P1 · kind: release · transport: contracts
- Started: 2026-11-26 · Finished: 2026-11-26
- Commits: `cae9342` (contracts workflow fix), `a842f66` (messaging workflow + vendored tarball), plus the coordinator closeout commits in `Documentation` and `state-for-agents`.

## What

All 15 repos with GitHub remotes were pushed under explicit user approval,
in dependency order: `ecom-contracts` and `ecom-messaging` first, the ten
service repos next, then `ecom-infra`, `Documentation`, `state-for-agents`.
Three repos had no upstream (`ecom-messaging`, `notify-svc`, `import-svc`) and
were set with `git push -u origin master`. `frontend/storefront` was pushed to
`staging` only, as directed; its local `main` was left untouched. A dry-run
push preceded every real push, and every repo ended at `ahead=0`, `behind=0`.

Five annotated tags were created from reviewed commits and pushed one at a
time:

| Tag | Commit | Release asset(s) |
|---|---|---|
| `v1.3.0` | `4383b26` | `ecom-contracts-1.3.0.tgz` |
| `v1.4.0` | `7c33d1d` | `ecom-contracts-1.4.0.tgz` |
| `v1.5.0` | `24204df` | `ecom-contracts-1.4.0.tgz`, `ecom-contracts-1.5.0.tgz` |
| `v2.0.0` | `cae9342` | `ecom-contracts-2.0.0.tgz` |
| `v0.6.0` (messaging) | `a842f66` | `ecom-messaging-0.6.0.tgz` |

Each `v*` push ran that repo's release workflow, which gates on typecheck,
tests and `pnpm pack`, checks that the tag matches `package.json`, then creates
the GitHub Release with `gh` and `GITHUB_TOKEN`. All five runs completed
`success`; the releases and their assets were verified through the GitHub API.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Fix the contracts workflow to attach one exact tarball | Eight older tarballs are tracked, so `./*.tgz` attached every version to every release | Leave the wildcard and publish mixed-version assets going forward |
| Vendor the contracts tarball into messaging for CI | The release workflow installs with `--frozen-lockfile`, and a single-repo checkout has no sibling tarball to resolve; a copied byte-identical file keeps the lockfile integrity valid | Cross-repo checkout with a token, or relaxing `--frozen-lockfile` |
| Push tags individually | A single push of four annotated tags produced **no** workflow runs here; re-pushing each tag separately triggered all four runs | Bulk `git push origin v1.3.0 v1.4.0 ...` / `git push --tags` |
| `v2.0.0` is lightweight, the three retro-tags are annotated | The first retry used a lightweight tag to isolate the trigger problem; re-annotating it would create a release that already exists | A second workflow run against an existing release |

## Verification

- `git push --dry-run` passed for all 15 repos before any real push.
- Every repo verified at `ahead=0` against its upstream after pushing.
- `ls-remote --tags` confirmed all five tags on the remote.
- GitHub Actions: six `release` runs in `ecom-contracts` (2 historical + 4 new),
  one in `ecom-messaging`; all `conclusion: success`.
- GitHub Releases API: all five releases present with the assets listed above.
- The old `v1.5.0` workflow still attaches the two tarballs tracked at that
  commit — a historical asset list, not a defect in the current workflow.

## Follow-ups

- `ecom-infra/ci/reusable-build.yml` checks out one repo while service pins
  use sibling `file:..\ecom-contracts\*.tgz` paths. Accepted as a documented
  follow-up: no installed CI workflow is broken by this push (search-svc
  vendors its tarball; the templates are not installed hooks). The release
  workflows are self-contained for the two library repos.
- The 13 live-stack tasks remain open; publishing does not verify them.
- No npm publish occurred — both packages are `"private": true`, so the
  distribution channel is GitHub Releases with attached tarballs.
