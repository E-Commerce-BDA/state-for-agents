# Task: ord-002 — DDL Schema Migration & Fixtures for order-svc

## Summary
- Created `db/001-order-schema.sql` defining 7 tables in PostgreSQL schema `order`:
  1. `orders`: lifecycle status machine, grand_total, financial fields, JSONB addresses snapshot, updated_at trigger, indexes.
  2. `order_items`: item lines with product_name, sku, unit_price, line_total, and options snapshots.
  3. `order_status_history`: timeline audit trail for status transitions with actor.
  4. `payments`: payment records with mock/stripe/paypal provider, status, unique transaction_id.
  5. `outbox`: transactional outbox pattern table with partial index `idx_outbox_pending`.
  6. `discount_codes`: coupons with percent/fixed types, bounds validation, max_uses, uses_count, and date window.
  7. `shipments`: fulfillment and tracking number tracking.
- Created `db/002-seed-orders.sql` with rich test fixtures (`SAVE10`, `FLAT20`, `EXPIRED50`, `MAXEDOUT`, `DISABLED5`, and sample order).
- Created `src/db/rows.ts` with strict TypeScript types mirroring all tables.
- Implemented and verified `test/schema.e2e-spec.ts` (8/8 tests passed covering table existence, unique constraints, check constraints, cascade deletes, and update triggers).
- 4 atomic commits recorded in `order-svc`.
