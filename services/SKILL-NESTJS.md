# SKILL-NESTJS — module shape per service

> Scope: NestJS 10 service skeleton (own repo). DB: raw `pg` for Postgres, Mongoose for Mongo.
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/2.Tech-Stack.md §5`, `services/auth.md` (shape model)

## Rules

1. Layout: `src/main.ts` (pino, `x-request-id`, ValidationPipe, Swagger `/docs`) → `app.module.ts` → `src/modules/<domain>/` (controller, service, repository) → `src/db/` (pool, rows, queries) → `src/messaging/` (`event-bus.interface`, `kafka-bus` for all domain events) → `src/tasks/` (`task-queue.interface`, `sqs-task-queue` for `send-email`, `process-row`, `resize-image`, `reminders`) → `src/common/` (JwtAuth, Roles, service-key guards, error filter, interceptors).
2. Controllers are thin: validate DTO (from `@ecom/contracts`) → call service → map to envelope. Business + SQL live in service/repository, never in controller.
3. Multi-write = transaction: `const client = await pool.connect(); try { await client.query('BEGIN'); …; await client.query('COMMIT'); } catch { await client.query('ROLLBACK'); throw; } finally { client.release(); }` (order + outbox same TX).
4. Never import sibling-service code or transport clients directly — inject `IEventBus`; never cross-schema SQL (see SKILL-POSTGRES #1).
5. Errors use shared `codes.ts` envelope `{code, message, requestId}`; log JSON with `requestId`; unhandled errors exit non-zero (watcher sees crash).

## Good vs bad

```ts
// GOOD — thin controller, service owns TX + bus
@Post('checkout') async checkout(@Body() dto: CheckoutDto) { return this.orders.checkout(dto); }
// service: BEGIN → validate → insert order + outbox → COMMIT → bus.publish(orderCreated(dto)) → return
// BAD — SQL + bus client + cross-service import inside controller
@Post('checkout') async checkout(@Body() dto: any) {
  await pool.query(`INSERT INTO orders ... '${dto.x}'`);       // injection + no TX
  await this.kafkaProducer.send(...);                           // direct transport import
}
```

> Note: structural-only until the first service build (auth-svc skeleton) — re-verify against real code then.

Use next: SKILL-POSTGRES (queries/TX), SKILL-INTERFACES (DTO types), SKILL-FUNCTIONS (small pure helpers).
