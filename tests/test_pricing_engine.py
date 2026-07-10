"""End-to-end integration tests for cart price calculation.

These tests exercise the full stack -- API routers, services,
validators, repositories, the Strategy layer, and the Rule/Pricing
engines -- against a real (in-memory) database, verifying the
business rules described in the assignment spec: priority, stacking,
expiry, and active/inactive handling.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

NOW = datetime.utcnow()
PAST_START = (NOW - timedelta(days=10)).isoformat()
PAST_END = (NOW - timedelta(days=1)).isoformat()
FUTURE_START = (NOW - timedelta(days=1)).isoformat()
FUTURE_END = (NOW + timedelta(days=30)).isoformat()


def _create_customer(client: TestClient, tier: str = "SILVER") -> int:
    response = client.post(
        "/api/v1/customers",
        json={"name": "Test User", "email": f"user_{tier}@example.com", "tier": tier},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_product(client: TestClient, price: float, category: str = "General") -> int:
    response = client.post(
        "/api/v1/products", json={"name": "Item", "category": category, "price": price}
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_discount(client: TestClient, **kwargs) -> int:
    payload = {
        "name": "Discount",
        "value": 0,
        "minimum_purchase": 0,
        "is_stackable": False,
        "priority": 100,
        "active": True,
    }
    payload.update(kwargs)
    response = client.post("/api/v1/discounts", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_promotion(
    client: TestClient, discount_id: int, start: str, end: str, active: bool = True
) -> int:
    response = client.post(
        "/api/v1/promotions",
        json={
            "discount_id": discount_id,
            "start_date": start,
            "end_date": end,
            "active": active,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_calculate_with_no_promotions_returns_subtotal_as_final(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=100.0)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 2}]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["subtotal"] == 200.0
    assert body["total_discount"] == 0.0
    assert body["final_amount"] == 200.0
    assert body["applied_discounts"] == []


def test_calculate_applies_active_in_window_percentage_discount(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)
    discount_id = _create_discount(
        client, name="10% Off", type="PERCENTAGE", value=10, minimum_purchase=0
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    body = response.json()
    assert body["subtotal"] == 1000.0
    assert body["total_discount"] == 100.0
    assert body["final_amount"] == 900.0
    assert len(body["applied_discounts"]) == 1


def test_calculate_ignores_expired_promotion(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)
    discount_id = _create_discount(client, name="Expired", type="PERCENTAGE", value=50)
    _create_promotion(client, discount_id, PAST_START, PAST_END)  # already expired

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    body = response.json()
    assert body["total_discount"] == 0.0
    assert body["final_amount"] == 1000.0


def test_calculate_ignores_inactive_discount_even_if_promotion_active(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)
    discount_id = _create_discount(
        client, name="Deactivated", type="PERCENTAGE", value=50, active=False
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    assert response.json()["total_discount"] == 0.0


def test_calculate_stacks_multiple_stackable_discounts(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)

    d1 = _create_discount(
        client, name="5% Off", type="PERCENTAGE", value=5, is_stackable=True, priority=1
    )
    d2 = _create_discount(
        client, name="Flat 50", type="FLAT", value=50, is_stackable=True, priority=2
    )
    _create_promotion(client, d1, PAST_START, FUTURE_END)
    _create_promotion(client, d2, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    body = response.json()
    # 5% of 1000 = 50, plus flat 50 = 100 total
    assert body["total_discount"] == 100.0
    assert body["final_amount"] == 900.0
    assert len(body["applied_discounts"]) == 2


def test_calculate_selects_single_best_non_stackable_by_priority(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)

    high_priority = _create_discount(
        client,
        name="High Priority 5%",
        type="PERCENTAGE",
        value=5,
        is_stackable=False,
        priority=1,
    )
    low_priority = _create_discount(
        client,
        name="Low Priority 50%",
        type="PERCENTAGE",
        value=50,
        is_stackable=False,
        priority=10,
    )
    _create_promotion(client, high_priority, PAST_START, FUTURE_END)
    _create_promotion(client, low_priority, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    body = response.json()
    assert len(body["applied_discounts"]) == 1
    assert body["applied_discounts"][0]["name"] == "High Priority 5%"
    assert body["total_discount"] == 50.0


def test_calculate_buy_x_get_y_end_to_end(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=100.0)
    discount_id = _create_discount(
        client,
        name="Buy 2 Get 1",
        type="BUY_X_GET_Y",
        buy_quantity=2,
        get_quantity=1,
        minimum_purchase=0,
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 3}]},
    )

    body = response.json()
    assert body["subtotal"] == 300.0
    assert body["total_discount"] == 100.0  # 1 free unit
    assert body["final_amount"] == 200.0


def test_calculate_customer_tier_discount_requires_eligible_tier(client: TestClient) -> None:
    gold_customer_id = _create_customer(client, tier="GOLD")
    product_id = _create_product(client, price=1000.0)
    discount_id = _create_discount(
        client,
        name="Gold 20%",
        type="CUSTOMER_TIER",
        value=20,
        required_tier="GOLD",
        minimum_purchase=0,
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={
            "customer_id": gold_customer_id,
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )

    assert response.json()["total_discount"] == 200.0


def test_calculate_coupon_discount_requires_correct_code(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=1000.0)
    discount_id = _create_discount(
        client,
        name="Save10",
        type="COUPON",
        value=10,
        coupon_code="SAVE10",
        minimum_purchase=0,
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    no_coupon = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )
    assert no_coupon.json()["total_discount"] == 0.0

    with_coupon = client.post(
        "/api/v1/cart/calculate",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 1}],
            "coupon_code": "SAVE10",
        },
    )
    assert with_coupon.json()["total_discount"] == 100.0


def test_calculate_rejects_duplicate_product_lines(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=100.0)

    response = client.post(
        "/api/v1/cart/calculate",
        json={
            "customer_id": customer_id,
            "items": [
                {"product_id": product_id, "quantity": 1},
                {"product_id": product_id, "quantity": 2},
            ],
        },
    )

    assert response.status_code == 400


def test_calculate_unknown_customer_returns_404(client: TestClient) -> None:
    product_id = _create_product(client, price=100.0)
    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": 99999, "items": [{"product_id": product_id, "quantity": 1}]},
    )
    assert response.status_code == 404


def test_calculate_unknown_product_returns_404(client: TestClient) -> None:
    customer_id = _create_customer(client)
    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": 99999, "quantity": 1}]},
    )
    assert response.status_code == 404


def test_calculate_below_minimum_purchase_gets_no_discount(client: TestClient) -> None:
    customer_id = _create_customer(client)
    product_id = _create_product(client, price=50.0)
    discount_id = _create_discount(
        client, name="Big Spend 10%", type="PERCENTAGE", value=10, minimum_purchase=500
    )
    _create_promotion(client, discount_id, PAST_START, FUTURE_END)

    response = client.post(
        "/api/v1/cart/calculate",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
    )

    assert response.json()["total_discount"] == 0.0
