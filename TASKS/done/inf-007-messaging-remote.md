# inf-007 — give ecom-messaging a git remote

- Repo: `ecom-infra` task; satisfied in `ecom-messaging`
- Phase: P5 · priority: P0 · kind: chore
- Started: 2026-11-26 · Finished: 2026-11-26
- Commit(s): `a842f66` (release workflow), all local commits pushed in the release train

## What

`ecom-messaging` had a remote URL configured but no upstream, so its commits
could not leave the machine. The release train added `origin/master` tracking
and pushed every local commit; the repo now resolves `@{u}` and reports
`ahead=0`, `behind=0`.

The tag/version guard in the new release workflow (`a842f66`) checks that
`v` + `package.json.version` equals the pushed tag before `gh release create`.
The `v0.6.0` workflow run completed green and the GitHub Release contains
`ecom-messaging-0.6.0.tgz`, so the committed package and the published tag agree.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| Push the git history, not just the tarball | A tarball alone loses the commit history and the reviewable changes | Copying the `.tgz` to the release only |
| Verify the tag against the package version in CI | A stale tarball is exactly how the earlier peer drift happened | Trusting the local build |

## Verification

- `git rev-parse @{u}` resolves to `origin/master` in `ecom-messaging`.
- `git rev-list --count @{u}..HEAD` = 0; working tree clean.
- GitHub Actions run `45771908621` (`v0.6.0`) — `conclusion: success`.
- GitHub Releases API: `v0.6.0` has asset `ecom-messaging-0.6.0.tgz`.

## Follow-ups

- None. The admin-app and CI sibling-tarball items are separate tasks.
