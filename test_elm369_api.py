"""Project ELM369 integration tests — JMR0824197846902 / JMR08241978202646902."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from elm369_api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "operational", "system": "ELM369 Matrix API"}


def test_api_influence():
    response = client.post("/influence", json={
        "reach": 1000000.0, "viral_velocity": 7.5, "sentiment_delta": 0.25,
    })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "influence_weight": 9375000.0}


@pytest.mark.parametrize("overrides", [
    {"reach": -500.0}, {"viral_velocity": -1.0}, {"sentiment_delta": -1.1},
    {"reach": 1e308, "viral_velocity": 1e308},
])
def test_api_influence_invalid(overrides):
    payload = {"reach": 100.0, "viral_velocity": 5.0, "sentiment_delta": 0.1}
    response = client.post("/influence", json={**payload, **overrides})
    assert response.status_code == 400


def test_api_logistics():
    response = client.post("/logistics", json={
        "origin": "Kokomo_Hub", "destination": "Fulfillment_Node_7",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["optimal_path"] == ["Kokomo_Hub", "Regional_Hub", "Fulfillment_Node_7"]
    assert data["cost_index"] == 5.0


@pytest.mark.parametrize("origin,destination", [
    ("unknown", "Fulfillment_Node_7"), ("Kokomo_Hub", "unknown"),
])
def test_api_logistics_unknown_node(origin, destination):
    response = client.post("/logistics", json={"origin": origin, "destination": destination})
    assert response.status_code == 400


def test_api_logistics_same_node():
    response = client.post("/logistics", json={"origin": "Kokomo_Hub", "destination": "Kokomo_Hub"})
    assert response.status_code == 200
    assert response.json()["optimal_path"] == ["Kokomo_Hub"]
    assert response.json()["cost_index"] == 0.0


def test_api_transaction():
    response = client.post("/transaction", json={
        "base_amount": 50000.0, "supply_volatility": 0.01, "demand_flux": 0.015,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    ledger = data["ledger"]
    assert ledger["executed_gross_amount"] == 51250.00
    assert ledger["charity_allocation_total"] == 512.50
    assert ledger["shriners_hospitals"] == round(512.50 / 3.0, 2)
    assert ledger["charity_shares"] == [170.83] * 3
    total = sum(Decimal(str(share)) for share in ledger["charity_shares"])
    assert total + Decimal(str(ledger["charity_rounding_adjustment"])) == Decimal("512.50")
    assert ledger["net_treasury_settlement"] == 50737.50


@pytest.mark.parametrize("overrides", [
    {"base_amount": -1.0}, {"supply_volatility": -2.0}, {"base_amount": 1e308},
])
def test_api_transaction_invalid(overrides):
    payload = {"base_amount": 50000.0, "supply_volatility": 0.01, "demand_flux": 0.015}
    assert client.post("/transaction", json={**payload, **overrides}).status_code == 400


def test_api_transaction_zero():
    response = client.post("/transaction", json={
        "base_amount": 0.0, "supply_volatility": 0.0, "demand_flux": 0.0,
    })
    assert response.status_code == 200
    assert response.json()["ledger"]["net_treasury_settlement"] == 0.0


@pytest.mark.parametrize("endpoint", ["/influence", "/logistics", "/transaction"])
def test_api_missing_fields(endpoint):
    assert client.post(endpoint, json={}).status_code == 422


@pytest.mark.parametrize("value", ['"NaN"', '"Infinity"', "1e309"])
@pytest.mark.parametrize("endpoint,body", [
    ("/influence", '"reach": VALUE, "viral_velocity": 5, "sentiment_delta": 0.1'),
    ("/transaction", '"base_amount": VALUE, "supply_volatility": 0, "demand_flux": 0'),
])
def test_api_nonfinite_inputs(endpoint, body, value):
    response = client.post(
        endpoint, content="{" + body.replace("VALUE", value) + "}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]
