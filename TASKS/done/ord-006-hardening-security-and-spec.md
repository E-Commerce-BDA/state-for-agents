# Task: ord-006 — Hardening, Security, Service Key & Specification Documentation for order-svc

## Summary
- Implemented `src/common/http/request-id.ts` for gateway `x-request-id` header extraction and fallback UUID generation.
- Implemented `src/common/filters/http-exception.filter.ts` producing standard `{ error: { code, message, details }, requestId, timestamp }` envelope, echoing `x-request-id` in response headers, and preserving `/health` probes.
- Implemented `src/common/guards/service-key.guard.ts` enforcing `x-service-key` on inter-service endpoints.
- Implemented `src/common/interceptors/cache-control.interceptor.ts` enforcing `Cache-Control: no-store` on all mutating HTTP methods.
- Implemented `src/internal/internal.controller.ts` and `src/internal/internal.module.ts` exposing `GET /internal/orders/:id` for internal services.
- Wired global filter, interceptor, and validation pipe in `src/main.ts`.
- Implemented `test/security.e2e-spec.ts` with 12 comprehensive security tests:
  - Error envelope and `x-request-id` tracing.
  - `Cache-Control: no-store` on mutations.
  - `ServiceKeyGuard` rejection (401) on missing/invalid key and acceptance with valid key.
  - Cross-customer order isolation (403 Forbidden).
  - Non-admin status update and refund rejection (403 Forbidden).
  - Prototype pollution and parameter tampering rejection (`VALIDATION_FAILED`).
  - SQL injection immunity on coupon and order lookup endpoints.
- Authored comprehensive service specification `Documentation/services/order.md` matching `auth.md` shape.
- Verification:
  - 45 unit tests passed across 5 test suites.
  - 60 e2e tests passed across 6 test suites (105 total passing tests).
  - 0 oxlint warnings / 0 errors on 65 files, clean nest build exit 0.
  - 6 atomic commits recorded for Phase 6.
