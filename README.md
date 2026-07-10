# Retail Discount Engine

A production-quality Retail Discount Engine built with **FastAPI**, **SQLAlchemy**, and the **Strategy Design Pattern** — inspired by the Shopper's Stop internship assignment.

The engine prices a shopping cart by evaluating every active, in-window promotion against it, then resolves the winning combination of discounts according to **stackability** and **priority** rules, returning the subtotal, applied discounts, total discount, and final payable amount.

---

## Features

- **Percentage Discounts** — e.g. 10% off the whole cart
- **Flat Discounts** — e.g. ₹200 off, capped at the subtotal
- **Buy X Get Y Free** — e.g. Buy 2 Get 1 Free, per product line
- **Category Discounts** — e.g. 20% off Apparel only
- **Customer Tier Discounts** — e.g. 15% off for Gold+ members
- **Coupon Discounts** — e.g. `WELCOME10` for 10% off
- **Multiple Promotions** evaluated simultaneously, each scheduled via a time-boxed `Promotion` window
- **Priority Resolution** — among non-stackable discounts, the lowest `priority` number wins (ties broken by highest discount amount)
- **Stackable Discounts** — all qualifying stackable discounts are summed together, then combined with the single best non-stackable discount

---

## Tech Stack

| Concern       | Choice                          |
|---------------|----------------------------------|
| Language      | Python 3.12+                     |
| Framework     | FastAPI                          |
| Database      | SQLite (dev), SQLAlchemy ORM     |
| Validation    | Pydantic v2                      |
| Testing       | Pytest + FastAPI `TestClient`    |
| Docs          | Swagger (auto-generated)         |

---

## Installation

```bash
# 1. Clone / unzip the project, then cd into it
cd retail-discount-engine

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app (creates retail_discount_engine.db automatically on startup)
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.

### Swagger / OpenAPI docs
- Swagger UI: **http://127.0.0.1:8000/docs**
- ReDoc: **http://127.0.0.1:8000/redoc**

### Running tests

```bash
pytest -v
```

Tests use an isolated **in-memory** SQLite database per test function (see `tests/conftest.py`), so they never touch `retail_discount_engine.db` and can be run repeatedly with no cleanup required.

---

## Project Structure

```
retail-discount-engine/
├── app/
│   ├── main.py                     # FastAPI app assembly, routers, lifespan, middleware
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (env-driven config)
│   │   ├── database.py              # SQLAlchemy engine/session/Base + get_db dependency
│   │   └── constants.py             # Enums: DiscountType, CustomerTier, ErrorCode
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── discount.py
│   │   ├── promotion.py
│   │   ├── cart.py
│   │   └── cart_item.py
│   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── customer.py / product.py / discount.py / promotion.py / cart.py / bill.py
│   ├── repositories/                # Data-access layer (Repository Pattern)
│   │   ├── customer_repository.py / product_repository.py
│   │   ├── discount_repository.py / promotion_repository.py / cart_repository.py
│   ├── services/                    # Business orchestration between API and repos/engine
│   │   ├── customer_service.py / product_service.py
│   │   ├── discount_service.py / promotion_service.py / cart_service.py
│   ├── strategies/                  # Strategy Pattern: one class per discount type
│   │   ├── base_strategy.py         # Abstract DiscountStrategy, CartContext, DiscountResult
│   │   ├── percentage_discount.py / flat_discount.py / buy_x_get_y.py
│   │   ├── category_discount.py / customer_tier_discount.py / coupon_discount.py
│   ├── engine/                      # The pricing "brain"
│   │   ├── strategy_factory.py      # Factory Pattern: DiscountType -> DiscountStrategy
│   │   ├── rule_engine.py           # Stackability + priority resolution
│   │   └── pricing_engine.py        # Orchestrates the full calculate() flow
│   ├── validators/                  # Stateful domain validation (DB-aware business rules)
│   │   ├── cart_validator.py / product_validator.py / discount_validator.py
│   ├── exceptions/
│   │   ├── custom_exception.py      # AppException hierarchy
│   │   └── handlers.py              # Global FastAPI exception handlers
│   ├── middleware/
│   │   └── logging.py               # Request logging middleware
│   ├── api/                         # FastAPI routers
│   │   ├── customer.py / product.py / discount.py / promotion.py / cart.py
│   └── utils/
│       ├── mapper.py / helper.py / logger.py
├── tests/                            # Pytest suite (unit + integration)
├── requirements.txt
└── README.md
```

### Architecture

```
HTTP Request
    │
    ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  API Routers │────▶│   Services   │────▶│  Repositories │──▶ SQLAlchemy / SQLite
│ (app/api)    │     │(app/services)│     │(app/repos)    │
└─────────────┘     └──────┬───────┘     └───────────────┘
                            │
                            ▼ (cart pricing only)
                     ┌──────────────┐     ┌────────────────┐
                     │PricingEngine │────▶│  RuleEngine    │
                     │(app/engine)  │     │ (stacking/     │
                     └──────┬───────┘     │  priority)     │
                            │             └────────────────┘
                            ▼
                    ┌────────────────┐     ┌──────────────────┐
                    │ StrategyFactory│────▶│ DiscountStrategy  │
                    │  (app/engine)  │     │  implementations  │
                    └────────────────┘     │ (app/strategies)  │
                                            └──────────────────┘
```

Each layer only depends on the layer directly beneath it (Clean Architecture / Dependency Rule):
- **Routers** never touch the database or business rules directly.
- **Services** never construct SQL — they delegate to **repositories**.
- **Strategies** never touch the database — they operate on plain in-memory `CartContext` objects, making them trivial to unit test.
- Adding a new discount type requires only: a new `DiscountType` enum value, a new `DiscountStrategy` subclass, and one line in `StrategyFactory` — the engine itself never changes (Open/Closed Principle).

---

## API Documentation

All routes are mounted under the `/api/v1` prefix.

### Customers

| Method | Path                     | Description              |
|--------|---------------------------|--------------------------|
| POST   | `/api/v1/customers`        | Create a customer         |
| GET    | `/api/v1/customers`        | List customers (paginated)|
| GET    | `/api/v1/customers/{id}`   | Get a customer            |
| PUT    | `/api/v1/customers/{id}`   | Partially update a customer |
| DELETE | `/api/v1/customers/{id}`   | Delete a customer         |

### Products

| Method | Path                     | Description              |
|--------|---------------------------|--------------------------|
| POST   | `/api/v1/products`         | Create a product          |
| GET    | `/api/v1/products`         | List products (paginated) |
| GET    | `/api/v1/products/{id}`    | Get a product             |
| PUT    | `/api/v1/products/{id}`    | Partially update a product|
| DELETE | `/api/v1/products/{id}`    | Delete a product          |

### Discounts

| Method | Path                     | Description              |
|--------|---------------------------|--------------------------|
| POST   | `/api/v1/discounts`        | Create a discount rule    |
| GET    | `/api/v1/discounts`        | List discount rules       |
| GET    | `/api/v1/discounts/{id}`   | Get a discount rule       |
| PUT    | `/api/v1/discounts/{id}`   | Partially update a discount |
| DELETE | `/api/v1/discounts/{id}`   | Delete a discount rule    |

### Promotions

| Method | Path                    | Description                          |
|--------|--------------------------|---------------------------------------|
| POST   | `/api/v1/promotions`      | Schedule a promotional window for a discount |
| GET    | `/api/v1/promotions`      | List all promotions                   |

### Cart

| Method | Path                       | Description                              |
|--------|-----------------------------|-------------------------------------------|
| POST   | `/api/v1/cart/calculate`     | Price a cart, applying every eligible discount |

---

## Example Requests & Responses

### 1. Create a customer

**Request** — `POST /api/v1/customers`
```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "tier": "GOLD"
}
```

**Response** — `201 Created`
```json
{
  "id": 1,
  "name": "Asha Rao",
  "email": "asha@example.com",
  "tier": "GOLD"
}
```

### 2. Create a product

**Request** — `POST /api/v1/products`
```json
{
  "name": "Wireless Mouse",
  "category": "Electronics",
  "price": 999.0
}
```

**Response** — `201 Created`
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "category": "Electronics",
  "price": 999.0
}
```

### 3. Create a discount rule (Buy 2 Get 1 Free)

**Request** — `POST /api/v1/discounts`
```json
{
  "name": "Buy 2 Get 1 Free",
  "type": "BUY_X_GET_Y",
  "buy_quantity": 2,
  "get_quantity": 1,
  "minimum_purchase": 0,
  "is_stackable": false,
  "priority": 1,
  "active": true
}
```

### 4. Schedule a promotion for that discount

**Request** — `POST /api/v1/promotions`
```json
{
  "discount_id": 1,
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-12-31T23:59:59",
  "active": true
}
```

### 5. Calculate a cart's final price

**Request** — `POST /api/v1/cart/calculate`
```json
{
  "customer_id": 1,
  "items": [
    { "product_id": 1, "quantity": 3 }
  ],
  "coupon_code": null
}
```

**Response** — `200 OK`
```json
{
  "customer_id": 1,
  "subtotal": 2997.0,
  "applied_discounts": [
    {
      "discount_id": 1,
      "name": "Buy 2 Get 1 Free",
      "type": "BUY_X_GET_Y",
      "amount": 999.0
    }
  ],
  "total_discount": 999.0,
  "final_amount": 1998.0
}
```

### Error response shape

Every error follows the same shape:
```json
{
  "error_code": "NOT_FOUND",
  "message": "Customer with id 999 not found."
}
```

| Status | error_code          | Meaning                                    |
|--------|----------------------|---------------------------------------------|
| 404    | `NOT_FOUND`           | Referenced resource does not exist          |
| 400    | `BAD_REQUEST`         | Well-formed but business-rule-invalid request (e.g. duplicate cart line, duplicate email/coupon code) |
| 422    | `VALIDATION_ERROR`    | Schema validation failure (missing/invalid field) |
| 500    | `INTERNAL_ERROR`      | Unexpected server error                     |

---

## Business Rules Implemented

- Minimum purchase threshold per discount
- Customer / product existence validation
- Promotion must be `active` **and** within `[start_date, end_date]`
- Underlying `Discount` must also be `active`, even if its `Promotion` window is open
- Quantity must be `> 0`, price must be `> 0`
- No duplicate product lines within a single cart-calculate request
- Coupon codes must be unique across discounts
- Stackable discounts combine (sum); among non-stackable discounts, the lowest `priority` number wins, with the highest discount amount as a tie-breaker

---

## Coding Standards

- **SOLID** principles throughout (Single Responsibility per layer, Open/Closed via Strategy + Factory, Dependency Inversion via constructor-injected repositories/sessions)
- **Repository Pattern** for all persistence access
- **Strategy Pattern** for discount calculation, **Factory Pattern** for strategy selection
- **Dependency Injection** via FastAPI's `Depends`
- Full **type hints** and **docstrings** on every public class/function
- PEP8-compliant formatting
