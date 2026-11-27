# adm-005 — Admin theme/navigation editors render a sandboxed storefront preview with BFF-minted token, versioned nested postMessage drafts, save/revert controls and --adm-* chrome isolation

- Repo: `admin-app`
- Verified: 2026-11-27
- Commit(s): 3f8622a

## What

Admin theme/navigation editors render a sandboxed storefront preview with BFF-minted token, versioned nested postMessage drafts, save/revert controls and --adm-* chrome isolation.

## Why

Merchant changes must be seen before publish without re-skinning the admin tool. Rejected: srcDoc or admin token substitution.

## Verification

Coordinator verified clean trees, author identity and gates. Storefront:
249 files / 1678 tests, lint 0 errors, tsc and webpack green. Admin: 123
tests, lint 0 errors, typecheck and build green.

## Follow-ups

- No live cross-repo E2E; storefront consumer is contract-tested only.
