# Task: ord-006 — Hardening, Security, Service Key & Specification Documentation for order-svc

## Objective
Finalize `order-svc` with production hardening:
- Global exception filter producing standardized `{ error: { code, message, details }, requestId, timestamp }` envelope and echoing `x-request-id`.
- Internal service-key guard enforcing `x-service-key` on internal endpoints.
- Global Cache-Control interceptor adding `no-store` on mutations and financial endpoints.
- Comprehensive security e2e tests (cross-tenant isolation, RBAC enforcement, replay attacks, forged identity headers, SQL injection resistance).
- Service specification document `Documentation/services/order.md` following `auth.md` shape.
- State synchronization in `tasks.json` and `STATUS.md`.
