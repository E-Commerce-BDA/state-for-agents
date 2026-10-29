# ec-002 — event payloads and topic registry (in progress)

## What

`@ecom/contracts` 1.4.0 gains the six payload schemas consumers need and one registry that
answers `type -> payload schema`, `type -> dlq`. Before this, the envelope was canonical but
`payload` was `z.record(z.string(), z.unknown())`, so drift could only be found in production.

## How

- `src/schemas/events.ts`: `userRegisteredPayloadSchema`, `cartUpdatedPayloadSchema`,
  `cartAbandonedPayloadSchema`, `orderCreatedPayloadSchema`,
  `orderStatusUpdatedPayloadSchema`, `pageViewedPayloadSchema` + inferred types.
- `src/schemas/topics.ts` (new): `eventTopicSchema` (11 names), `EVENT_TOPICS` (producer,
  consumers, partitions, retention, key, dlq), `eventPayloadSchemas`, `parseEventPayload`,
  `dlqTopicName`.
- `src/index.ts` export, `test/events.spec.ts`, `package.json` 1.4.0, CHANGELOG, README.

## Decisions

1. **Mirror the producer, not the ideal.** `cart.updated` is built from `buildCartUpdatedEvent`
   + `toItemDto`, so it carries `id`, `addedAt`, and nullable `variantId`/`productSlug`/
   `imageUrl`/`variantLabel`; `userId`/`sessionId` are required-but-nullable because the
   `CartUpdatedEvent` interface declares `string | null`.
   Rejected: a slim "canonical" cart payload — it would reject every real guest-cart event.
2. **No email in `user.registered`.** au-004 already decided PII minimization and au-005 adds
   `GET /internal/users/:id/email`. Rejected: embed the address, which spreads PII across
   topics and logs.
3. **`reservationId: uuid.or(literal(''))`.** The checkout resume path passes
   `order.stock_reservation_id ?? ''`. Rejected: drop the field — the consumer needs the hold id.
4. **`refundAmount` stays `string | number`.** Postgres `DECIMAL` arrives as `string`; a JS
   producer would send `number`. Both are tested; normalizing the producer is a follow-up.
5. **`cart.abandoned` and `page.viewed` are target contracts.** analytics-svc does not exist
   yet, so they document the intended shape (matching `/analytics/events/page-view`).
6. **Strict everywhere.** `.strict()` makes an unknown key a validation error, which is the
   point of the task.

## Verification

| Check | Result |
|---|---|
| `pnpm build` | pending |
| `pnpm typecheck` | pending |
| `pnpm test` | pending |
| `pnpm pack` → `ecom-contracts-1.4.0.tgz` | pending |

## Open

- ec-005 must include 1.4.0/1.5.0 in the release train.
- Normalize `refundAmount`; replace `reservationId: ''` at the source.
