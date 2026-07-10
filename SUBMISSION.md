# Submission Notes — Retail Discount Engine

## Time Spent

| Phase | Time Spent |
|---|---|
| Understanding requirements / planning architecture | _fill in_ |
| Setting up project structure (models, schemas, repositories) | _fill in_ |
| Implementing discount strategies (Strategy Pattern) | _fill in_ |
| Implementing Rule Engine (stackability + priority logic) | _fill in_ |
| Implementing Pricing Engine (orchestration) | _fill in_ |
| Building API layer (routers, services) | _fill in_ |
| Writing tests | _fill in_ |
| Debugging (env setup, FastAPI 204 response_model bug, etc.) | _fill in_ |
| **Total** | _fill in_ |

## Assumptions Made

- **Non-stackable discount tie-breaking**: when multiple non-stackable discounts qualify at the same priority level, the one with the highest discount amount is chosen, since the spec didn't explicitly define a tie-breaker.
- **Buy X Get Y is evaluated per product line**, not across the whole cart — i.e. the free units always come from the same product being bought in bulk, not a different (cheaper) product substituted in.
- **Coupon code matching is case-insensitive** and whitespace is trimmed, since the spec didn't specify exact matching behavior and this is closer to typical real-world coupon UX.
- **Customer tier discounts use a strict ranking** (Silver < Gold < Platinum), where a customer's tier must be *at least* the discount's required tier — a Platinum customer is assumed eligible for a Gold-tier discount.
- **A flat discount is capped at the cart subtotal**, so the final payable amount can never go negative.
- **Promotions are only evaluated if both the promotion window is active *and* the underlying discount itself is marked active** — a promotion whose linked discount has been deactivated is treated as inactive even if its date window is still open.
- **Default database is SQLite**, chosen for simplicity in local development and grading; the repository layer is written against the SQLAlchemy ORM so swapping to Postgres/MySQL would mainly be a connection-string change.

## Known Limitations

- **No authentication/authorization** — all endpoints are open. In a real production system, creating discounts/promotions would be an admin-only action.
- **No pagination** on list endpoints (`GET /customers`, `GET /products`, etc.) — fine for test/demo data volumes, but would need to be added for a large catalog.
- **Buy X Get Y does not account for cross-product bundling** (e.g. "buy 2 shirts, get 1 pair of socks free") — it only supports same-product bulk discounts.
- **No concurrency handling** for coupon usage limits (e.g. a coupon marked "single use" could theoretically be used twice under simultaneous requests) — not currently a modeled feature, but would need row-level locking if added.
- **`datetime.utcnow()` deprecation warnings** appear in test output (Python 3.12+ deprecates this in favor of timezone-aware datetimes). Doesn't break functionality but should be cleaned up.
- **SQLite is not ideal for concurrent write-heavy production use** — fine for this assignment/demo scope.

## What I Would Improve With More Time

- Add **JWT-based authentication** and role-based access control (admin vs. customer-facing endpoints).
- Add **pagination, filtering, and sorting** to all list endpoints.
- Extend the **Buy X Get Y strategy** to support cross-product bundles.
- Add **coupon usage tracking** (max redemptions, per-customer limits) with proper concurrency-safe updates.
- Replace `datetime.utcnow()` with timezone-aware `datetime.now(datetime.UTC)` throughout.
- Add **integration with a real database** (Postgres) with Alembic migrations instead of SQLite auto-create.
- Add **structured logging and request tracing** for easier debugging in production.
- Add **rate limiting** on the cart calculation endpoint to prevent abuse.
- Write **property-based tests** (e.g. with Hypothesis) for the Rule Engine's stackability logic to catch edge cases beyond the hand-written test cases.
