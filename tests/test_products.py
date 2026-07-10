"""Tests for the Product resource (API + service layer behavior)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_product_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={"name": "Wireless Mouse", "category": "Electronics", "price": 999.0},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Wireless Mouse"
    assert body["category"] == "Electronics"
    assert body["price"] == 999.0
    assert "id" in body


def test_create_product_rejects_non_positive_price(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={"name": "Broken Item", "category": "Misc", "price": 0},
    )
    assert response.status_code == 422


def test_get_product_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/products/9999")
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


def test_list_products_returns_created_items(client: TestClient) -> None:
    client.post("/api/v1/products", json={"name": "A", "category": "Cat1", "price": 10.0})
    client.post("/api/v1/products", json={"name": "B", "category": "Cat2", "price": 20.0})

    response = client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_update_product_partial(client: TestClient) -> None:
    created = client.post(
        "/api/v1/products", json={"name": "Old Name", "category": "Cat", "price": 50.0}
    ).json()

    response = client.put(f"/api/v1/products/{created['id']}", json={"price": 75.0})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Old Name"
    assert body["price"] == 75.0


def test_delete_product(client: TestClient) -> None:
    created = client.post(
        "/api/v1/products", json={"name": "Temp", "category": "Cat", "price": 5.0}
    ).json()

    delete_response = client.delete(f"/api/v1/products/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/products/{created['id']}")
    assert get_response.status_code == 404
