# cms-003 — media key containment and file access

- Repo: `cms-svc` + `ecom-contracts` (1.5.0) + `Documentation`
- Phase: P0 · kind: security · transport: HTTP
- Started: 2026-10-30 · Finished: 2026-10-30

## What the defect was

`GET /cms/media/file/*` took the rest of the URL, ran
`path.resolve(baseDir, key)`, and served whatever existed at that path. Three
consequences:

1. `..`, an encoded separator, or an absolute path escaped the storage root.
2. Any file under `storage/` was served, whether or not a `cms_media` row
   existed, and with no authentication.
3. There was no way to store an editorial asset that is not public.

## How it was fixed

### contracts 1.5.0

- `mediaVisibilitySchema = z.enum(['public','private'])`, `MediaVisibility`.
- `mediaSchema.visibility` is **optional** (absent = public), so 1.5.0 stays a
  true MINOR and every 1.4.0 payload still parses.
- Compatibility checked before shipping: `mediaSchema` is parsed only in
  `ecom-contracts/test/contracts.spec.ts`; no cms-svc, storefront, or admin code
  imports it. The package is additive for every pinned consumer.

### cms-svc

- `StoragePort`: `getFilePath` → `resolvePath(key): Promise<string>`, plus
  `InvalidMediaKeyError`. The port no longer hands out an unchecked path.
- `LocalDiskStorageAdapter`: one **private** `resolveKey` builder for every
  operation (`save`, `delete`, `exists`, `resolvePath`): reject a null byte →
  `decodeURIComponent` exactly once → `mediaKeySchema.safeParse` → `path.resolve`
  → `path.relative` containment. `resolvePath` then repeats the containment
  check on `fs.realpath` of both the root and the target, which defeats a symlink
  planted inside `storage/`.
- `MediaService`: `getStorage()` deleted; `findByKey`, `findById`,
  `streamablePath(key, 'public' | 'admin')`. The public viewer resolves the row
  first and returns `MEDIA_NOT_FOUND` for a private or missing row **before**
  touching the disk, so the route is not an existence oracle. A storage
  rejection is mapped to the same generic 404.
- `MediaController`: the open route keeps its path, now serves `public` rows
  only, `stat`s the real path before the first header, and sends `Content-Type`
  from the stored MIME, `nosniff`, `inline`, and
  `Cache-Control: public, max-age=60, must-revalidate`. The new
  `GET /cms/admin/media/:id/file` is admin-guarded, takes a Mongo `ObjectId`
  (a key contains slashes and cannot be one route segment), serves any
  visibility, and sends `private, no-store`.
- `cms_media.visibility` (enum, default `public`, indexed); `uploadMedia` accepts
  `visibility` and rejects an unknown value with `400 VALIDATION_FAILED`;
  `getAdminMedia` filters by `visibility`.
- `pnpm` repin `1.1.0 → 1.5.0`; one type error surfaced
  (`blogs.service.ts` `deleted.toObject()` cast) and was fixed in the same
  commit.

## Decisions and the alternatives that were rejected

| Decision | Reason | Rejected alternative |
|---|---|---|
| Containment in one private builder, reached by every operation | A second path builder is a second bypass | Sanitising the string in the controller (bypassable with `%2e%2e`, `\`, mixed separators) |
| Re-validate after `fs.realpath` | Lexical containment cannot see a symlink planted inside the root | `path.resolve` only (the original defect) |
| Public route answers **404** for a private row | A 403 confirms the asset exists; 404 keeps private files unenumerable | 401/403 on the public route |
| Private delivery through a separate admin route keyed by `ObjectId` | Keys contain `/`; an admin route also keeps the public route cacheable and anonymous | Signed URLs (needs a key pair and expiry policy; deferred, no consumer yet) |
| `max-age=60, must-revalidate`, not `immutable` | Visibility is mutable; `immutable` would pin public bytes after privatisation | `immutable, max-age=31536000` (needs a versioned URL first) |
| `visibility` optional in the contract, defaulted in the service | Keeps 1.5.0 a MINOR; old documents have no field | Required field (would break every stored document and 1.4.0 payload) |
| A `cms_media` row is required to serve bytes | Closes "any file on disk is public" | Serving by path existence (the original defect) |

## Verification

| Gate | Result |
|---|---|
| contracts `pnpm build` / `typecheck` / `test` / `pack` | green · 88 tests · `ecom-contracts-1.5.0.tgz` |
| `mediaSchema` grep | parsed only in `contracts.spec.ts` |
| cms-svc `pnpm typecheck` | clean |
| cms-svc `pnpm lint` | 0 warnings, 0 errors (83 files) |
| cms-svc `pnpm test` | 115 passed (18 files) |
| cms-svc `pnpm test:e2e` | 70 passed (6 files, Mongo on `:27018`) |
| cms-svc `pnpm build` | clean |

Evidence the defect is closed:

- `local-disk.storage.spec.ts` rejects literal `../`, `%2e%2e%2f`, `%2e%2e%5c`,
  `media/2026/10/../../x.png`, `/etc/passwd`, `C:\Windows\win.ini`, a null byte,
  a `.svg`, a missing prefix, a broken escape, and an empty key — and asserts
  `save`/`delete` refuse them too. A symlink to a file outside the root is
  rejected (skipped when Windows refuses `fs.symlink` with `EPERM`).
- `media-security.e2e-spec.ts` (17 cases): seven HTTP traversal vectors answer
  `404 MEDIA_NOT_FOUND / File not found` with no `storage`, `media/`, `\` or temp
  path in the body; a file written into `storage/` with no row is 404; a private
  upload is 404 on the public route and 200 on the admin route; the admin route
  is 401 anonymous and 403 for a customer; a non-ObjectId id is 404; the public
  route sends `public, max-age=60, must-revalidate`; the admin route sends
  `private, no-store`; deletion closes both routes.
- `media.e2e-spec.ts` (the pre-existing suite) passes unchanged.

Acceptance wording: "private media returns 401/403 without a valid session" is
satisfied on the admin route (401 anonymous, 403 non-admin); the public route
deliberately answers 404 so it cannot be used to enumerate private assets.

## Commits

- `ecom-contracts` — `feat(contracts): add media visibility for 1.5.0`,
  `chore(release): 1.5.0`
- `cms-svc` — `chore(media): pin contracts 1.5.0`,
  `feat(media): contain storage keys and enforce visibility on delivery`,
  `test(media): cover traversal, visibility, and admin file access`
- `Documentation` — `docs(media): document the public and private delivery policies`

The planned `refactor(media): make resolveKey the only path builder` commit was
folded into the `feat(media)` commit: the port, the adapter, the service, and the
route form one security boundary, and any split leaves a commit whose tree does
not compile.

## Open

- `cms-004` still owns upload hardening: the size check runs after buffering,
  MIME comes from the client header, and `STORAGE_LOCAL_DIR` is not validated at
  boot. A private upload therefore still trusts the request.
- No signed-URL path exists; a CDN or the storefront cannot fetch a private asset
  without an admin token. Needed before private assets are shown on a public page.
- Resized variants are a trap for `cms-006`: `cms-svc` only *publishes*
  `media.resize-image`, and `mediaKeySchema` allows strictly
  `media/{yyyy}/{mm}/{hex-or-dash}.{png|jpg|webp|avif}`, so a future
  `.../0190a1b2-….png_320.webp` key is rejected by containment and must be
  either contracted as its own shape or served from its own resolver.
- `cms_media.visibility` has no backfill: existing documents are read as public,
  which is the intended default but should be written once with an update.
