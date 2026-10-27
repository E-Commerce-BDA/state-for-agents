# Task: ord-005 — Order Lifecycle, History & Status State Machine for order-svc

## Objective
Implement customer order history lookup, admin order management, finite status transition state machine, refund processing, and the asynchronous outbox relay worker.

## Plan
1. Strict DTOs:
   - `src/orders/dto/update-order-status.dto.ts`
   - `src/orders/dto/refund-order.dto.ts`
   - `src/orders/dto/order-query.dto.ts`
2. Finite State Machine:
   - `src/orders/order-state-machine.ts` defining allowed transitions and validation.
3. Orders Repository:
   - `src/orders/orders.repository.ts` with customer pagination, detailed order lookup with items & history, admin filtering, transactional status update with history & outbox entry, and refund processing.
4. Orders Service:
   - `src/orders/orders.service.ts` with RBAC authorization, state transition enforcement, and refund rules.
5. Outbox Subsystem:
   - `src/outbox/outbox.repository.ts` utilizing partial index `idx_outbox_pending`.
   - `src/outbox/outbox-relay.service.ts` polling and dispatching events to bus / log.
6. Orders Controller:
   - `src/orders/orders.controller.ts` with customer `GET /me/orders`, `GET /orders/:id`, and admin endpoints (`GET /orders`, `GET /orders/:id/status-history`, `PATCH /orders/:id/status`, `POST /orders/:id/refund`).
7. Tests & Verification:
   - Unit tests: `src/orders/orders.service.spec.ts`
   - E2E tests: `test/orders.e2e-spec.ts`
   - Zero oxlint errors, clean nest build, atomic commits.
