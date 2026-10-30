# cms-004 — media upload guards, magic-byte MIME, storage root validation

- Repo: `cms-svc` (+ `Documentation`)
- Phase: P0 · kind: security · transport: HTTP
- Started: 2026-10-30 · Finished: 2026-10-30

## What the defect was

Three holes on one route, `POST /api/v1/cms/admin/media`:

1. `FileInterceptor('file')` was created with **no `limits`**, so multer buffered
   the whole body in memory. A 1 GB upload was rejected only after it was
   already in RAM.
2. The stored type was whatever the client put in the multipart `Content-Type`
   header — a text file declared `image/png` was written to disk as a `.png`.
   `sizeBytes` also trusted the client's `size` field when present.
3. `STORAGE_LOCAL_DIR` was never validated: a relative value resolved against
   the process CWD, so uploads could land outside the repo, and an unwritable
   root failed on the first upload instead of at boot.

## How it was fixed

### The size decision happens before the body

- `UploadSizeGuard` reads `Content-Length` only and answers
  `413 MEDIA_TOO_LARGE` above `10 MB + 16 KB` of multipart overhead. It runs as
  a route guard, i.e. before the interceptor, so nothing is buffered.
- `FileInterceptor` now carries `limits: { fileSize: 10 MB, files: 1, fields: 8,
  parts: 12, fieldSize: 8 KB }` — the backstop for a chunked request that sends
  no `Content-Length`, which the guard explicitly passes through.
- Nest maps multer's `LIMIT_FILE_SIZE` to `PayloadTooLargeException`
  (`@nestjs/platform-express/multer/multer/multer.utils.js:94`), so
  `MediaTooLargeFilter` (`@Catch(PayloadTooLargeException)`) re-labels both
  sources as `{ code: 'MEDIA_TOO_LARGE' }`.
- A route-scoped filter **replaces** the global one for that handler, so the
  filter delegates the envelope to `HttpExceptionFilter` instead of
  duplicating it (verified: `requestId`, `timestamp`, `x-request-id` intact).

### The bytes are authoritative

- `media-signature.ts` sniffs PNG (`89 50 4E 47 0D 0A 1A 0A`), JPEG
  (`FF D8 FF`), WebP (`RIFF` at 0 **and** `WEBP` at 8), and AVIF (`ftyp` at 4
  with brand `avif`/`avis`). A shorter buffer, a `RIFF` that is not `WEBP`, or a
  `heic`/`mif1` brand returns `null`.
- `uploadMedia` order: empty buffer → `buffer.length > 10 MB` (413) → sniff
  (`null` = `MEDIA_TYPE_UNSUPPORTED`) → declared type outside the allowlist
  (`MEDIA_TYPE_UNSUPPORTED`) → declared ≠ sniffed (`MEDIA_TYPE_MISMATCH`).
- The stored `mimeType`, the extension (`EXTENSION_BY_MIME`), and `sizeBytes`
  come from the buffer. `resolveExtension` lost its unreachable filename
  fallback.

### The storage root is proven at boot

- `LocalDiskStorageAdapter implements OnModuleInit`: a relative
  `STORAGE_LOCAL_DIR` throws, `mkdir -p` creates the root, `W_OK` is required,
  and either failure aborts boot. The constructor is unchanged, so specs can
  still construct an adapter without side effects.
- `STORAGE_LOCAL_DIR` is optional in development and required in production in
  `env.validation.ts`; `.env.example` documents it; `storage*/` is gitignored;
  `test/setup-env.ts` gives every suite an `os.tmpdir()` root (the media suites
  still override it with their own).

## Decisions and the alternatives that were rejected

| Decision | Reason | Rejected alternative |
|---|---|---|
| `Content-Length` guard **plus** `multer limits.fileSize` | The guard answers from headers alone; multer still holds for chunked uploads without the header, so peak RAM is ≤ 10 MB either way | Stream to a temp file and rename — a new `StoragePort` method, temp lifecycle, and a rewrite of 185 fixtures |
| Sniffed bytes win, a disagreeing header is rejected | The header is exactly the attack surface this task exists to close, and the sniff also fixes the extension | Trust the header, sniff only for unknown extensions |
| Re-label through the existing `HttpExceptionFilter` | A route filter replaces the global one, so re-implementing the envelope would fork the error contract | A second full envelope implementation in the media module |
| Discard the in-flight body before answering the 413 (capped at 4× the ceiling) | Answering mid-upload closes the socket under the writer and the client sees `ECONNRESET` instead of the 413; discarding costs no RAM | Answer immediately and accept the reset; or drain without a cap, which lets one sender hold a socket for a gigabyte |
| `STORAGE_LOCAL_DIR` required only in production | Same shape as cart-svc's `INTERNAL_SERVICE_KEY`: the dev fallback can never reach production, and compose/e2e keep working | Always required — breaks the existing local setup for no security gain |

## Verification

- `pnpm typecheck` exit 0, `pnpm lint` **0 warnings / 0 errors** (90 files),
  `pnpm build` exit 0.
- `pnpm test`: **20 files, 133 tests green** (was 115 — the sniffer, the guard,
  the service cases, and the boot check are new).
- `pnpm test:e2e` (Mongo on 27018): **7 files, 75 tests green**, including the
  new `media-upload-limits.e2e-spec.ts`:
  - 11 MB attach → `413 MEDIA_TOO_LARGE` with the documented message;
  - `this is plainly not a png` declared `image/png` → `400 MEDIA_TYPE_UNSUPPORTED`;
  - PNG bytes attached as `renamed.jpg` / `image/jpeg` → `400 MEDIA_TYPE_MISMATCH`;
  - a real 45-byte PNG → `201` with `mimeType: 'image/png'`, `sizeBytes: 45`, and
    a `.png` key;
  - anonymous upload → `401` (auth runs before the size check).
- `media.e2e-spec.ts` and `media-security.e2e-spec.ts` pass unchanged: both
  already uploaded a real 45-byte PNG. The SVG case still answers `400`
  (`MEDIA_TYPE_UNSUPPORTED`), now from the sniff rather than from the header.
- Behaviour discovered while testing: answering a 413 without consuming the body
  produced `read ECONNRESET` in the client (`supertest` writes the whole body
  before it reads). That is what the drain-then-answer branch and the 4× cap
  exist for; the anonymous-upload test therefore asserts `401` on a small body
  (proving auth ordering) because the auth layer does not drain.
- No push, tag, or release.

## Open

- `cms-005` (outbox), `cms-006` (`cms.updated` on the wrong topic), `cms-007`
  (`media-resize-image` on Kafka instead of SQS) are untouched follow-ups.
- EXIF re-encoding and pixel-dimension capture are not part of this task; the
  stored `width`/`height` remain unset.
