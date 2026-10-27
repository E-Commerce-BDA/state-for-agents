# Task: ord-003 — Discount Codes & Pricing Subsystem for order-svc

## Summary
- Implemented strict DTOs for coupon validation, creation, updating, and querying:
  - `ValidateDiscountCodeDto`: strict non-optional `code: string` and `cartTotal: number`.
  - `CreateDiscountCodeDto`: strict non-optional `code`, `discountType ('percent' | 'fixed')`, `value`, optional `minOrderAmount`, `maxUses`, `startsAt`, `endsAt`, `isActive`.
  - `UpdateDiscountCodeDto`: partial coupon update DTO.
  - `DiscountQueryDto`: pagination with `page` and `perPage`.
- Implemented `DiscountsRepository` with raw SQL queries for lookup, validation, atomic usage increments, and admin CRUD.
- Implemented `DiscountsService`:
  - Normalized uppercase trim lookup.
  - Expiration window checks (`starts_at` and `ends_at`).
  - Max usage limits (`uses_count < max_uses`).
  - Minimum order amount threshold check.
  - Accurate pricing calculations: percentage bounded to 100%, fixed discount clamped to cart total, rounded to 2 decimal places.
- Implemented `DiscountsController` exposing `POST /discount-codes/validate` (public/customer) and admin CRUD endpoints gated by `@Roles('admin')`.
- Implemented cross-service auth: `JwtAuthGuard`, `RolesGuard`, `@Roles()` decorator, and `access-token.ts` verification.
- 17 unit tests passed in `discounts.service.spec.ts` (21 total unit tests).
- 14 e2e tests passed in `discounts.e2e-spec.ts` (24 total e2e tests across 3 files).
- 16 atomic commits recorded in `order-svc`.
