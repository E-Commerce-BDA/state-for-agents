# SKILL-POSTGRES — raw SQL via `pg` (production-grade)

> Scope: all Postgres access. No ORM. No migrations in v1 (schema applied manually).
> Status: Active | Date: 2026-09-30 | Parent: `Documentation/3.Database-Schema.md`

## Rules

1. One `Pool` per service (`src/db/pool.ts`), own schema only (`SET search_path` or qualified `catalog.products`). Never touch another service's tables.
2. **Parameterized always:** `pool.query('SELECT * FROM catalog.products WHERE slug = $1', [slug])`. String interpolation of values is a bug, fails review.
3. Hand-mirror column types from `3.Database-Schema.md` into TS row types (`src/db/rows.ts`); keep `DECIMAL` as string, compare in SQL.
4. One round trip per render: single JOIN for cart-with-items / PDP-with-images (never N+1). Check `EXPLAIN` for every new query touching p99 paths (cart/PDP/suggest).
5. Transactions for multi-write: `BEGIN` → order + outbox insert → `COMMIT` (see SKILL-NESTJS). Always `ROLLBACK` + `client.release()` in `finally`.
6. UUIDv7 in app code for new ids (time-ordered, Kafka-safe); money `>= 0` enforced by `CHECK`, validate before insert for good 400s.
7. Layout per service: `src/db/pool.ts`, `src/db/rows.ts`, `src/db/queries/<domain>.sql.ts` (named `const ... = \`SELECT ... $1\`` + typed function each).

## Good vs bad

```ts
// GOOD — parameterized, typed, single round trip
export async function getProductBySlug(pool: Pool, slug: string): Promise<ProductRow | null> {
  const { rows } = await pool.query<ProductRow>(
    `SELECT p.*, b.name AS brand_name FROM catalog.products p
     LEFT JOIN catalog.brands b ON b.id = p.brand_id
     WHERE p.slug = $1 AND p.deleted_at IS NULL`, [slug]);
  return rows[0] ?? null;
}
// BAD — interpolation (SQL injection), SELECT *, no schema guard
export async function getProductBySlug(pool: Pool, slug: string) {
  const { rows } = await pool.query(`SELECT * FROM products WHERE slug = '${slug}'`);
  return rows[0];
}
```

Use next: SKILL-NESTJS (transactions/outbox), SKILL-INTERFACES (row types), SKILL-REDIS (cache-aside).
