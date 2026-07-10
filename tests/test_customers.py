"""Tests for the Customer resource (API + service layer behavior)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_customer_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        json={"name": "Asha Rao", "email": "asha@example.com", "tier": "GOLD"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Asha Rao"
    assert body["tier"] == "GOLD"


def test_create_customer_duplicate_email_rejected(client: TestClient) -> None:
    payload = {"name": "Asha Rao", "email": "dup@example.com", "tier": "SILVER"}
    first = client.post("/api/v1/customers", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/customers", json=payload)
    assert second.status_code == 400
    assert second.json()["error_code"] == "BAD_REQUEST"


def test_default_tier_is_silver(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers", json={"name": "No Tier", "email": "notier@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["tier"] == "SILVER"


def test_get_customer_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/customers/12345")
    assert response.status_code == 404


def test_update_customer_tier(client: TestClient) -> None:
    created = client.post(
        "/api/v1/customers",
        json={"name": "Ravi", "email": "ravi@example.com", "tier": "SILVER"},
    ).json()

    response = client.put(f"/api/v1/customers/{created['id']}", json={"tier": "PLATINUM"})
    assert response.status_code == 200
    assert response.json()["tier"] == "PLATINUM"


def test_delete_customer(client: TestClient) -> None:
    created = client.post(
        "/api/v1/customers",
        json={"name": "Temp", "email": "temp@example.com", "tier": "SILVER"},
    ).json()

    delete_response = client.delete(f"/api/v1/customers/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/customers/{created['id']}")
    assert get_response.status_code == 404
