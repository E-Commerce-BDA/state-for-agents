# SKILL-REDIS — what lives in Redis and how

> Scope: cache, sessions, rate limits, idempotency, compare tray. Redis is never source of truth.
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/1.Architecture.md §11`, `3.Database-Schema.md`

## Rules

1. Key formats + TTLs (fixed — never invent keys):
   `cat:product:{id}` / `cat:list:{queryHash}` (5m), `cms:section:{key}` (5m),
   `cms:settings:global` (1m), `cms:nav` (5m), `search:suggest:{q}` (10m),
   `sess:{tokenId}` (sliding), `idem:{userId}:{route}:{key}` (24h) and
   `idem:{userId}:{route}:{key}:lock` (short), `rate:{ip}:{route}` (window),
   `compare:{sessionId}` (session).
2. Pattern is always cache-aside: read cache → miss → read DB → write cache with TTL → return. Invalidate on events (`product.imported`, `cms.updated` via `IEventBus`), never by timer guessing.
3. Sessions: refresh-token lookup Redis first, Postgres fallback (Redis-down = slower but correct). Idempotency: the **domain row is the authority** — the key is persisted on the record it protects (e.g. `order.orders (user_id, idempotency_key)` unique), Redis only caches the response for replay. Scoping the key by user and route is mandatory: a bare `idem:{key}` lets one user replay another user's stored response.
4. Rate limits live in Redis counters; bypass-open on Redis-down is accepted v1 (document it, don't silently fail closed).
5. Client: `ioredis`; one client per service; prefix keys per env (`prod:`) to avoid collisions.

## Good vs bad

```ts
// GOOD — aside with invalidation boundary
async function getProduct(id: string) {
  const hit = await redis.get(`cat:product:${id}`);
  if (hit) return JSON.parse(hit);
  const row = await db.getProductById(id);       // Postgres truth
  if (row) await redis.set(`cat:product:${id}`, JSON.stringify(row), 'EX', 300);
  return row;
}
// BAD — cache as truth, no TTL, invented key
async function getProduct(id: string) {
  return JSON.parse(await redis.get(`product_${id}`));  // null after eviction = fake 404
}
```

> Note: structural-only until the first cache/session keys land — re-verify against real code then.

Use next: SKILL-NESTJS (guards/interceptors), SKILL-POSTGRES (truth queries).
