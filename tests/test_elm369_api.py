import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient

from elm369_api import app
from elm369_matrix_engine import (
    FinancialTransactionConfig,
    calculate_influence_weight,
    initialize_logistics_network,
    optimize_logistics_route,
    process_financial_simulation,
)


class MatrixEngineTests(unittest.TestCase):
    def test_influence_calculation_and_validation(self):
        self.assertEqual(calculate_influence_weight(10, 2, 0.5), 30)
        with self.assertRaises(ValueError):
            calculate_influence_weight(10, 2, 1.5)

    def test_logistics_chooses_least_cost_route(self):
        path, cost = optimize_logistics_route(
            initialize_logistics_network(), "Kokomo", "Cincinnati"
        )
        self.assertEqual(path, ["Kokomo", "Indianapolis", "Cincinnati"])
        self.assertEqual(cost, 3.0)
        self.assertEqual(
            optimize_logistics_route(initialize_logistics_network(), "Chicago", "Chicago"),
            (["Chicago"], 0.0),
        )

    def test_financial_simulation_rounds_and_allocates_one_percent(self):
        ledger = process_financial_simulation(
            FinancialTransactionConfig(100, 0.1, 0.2)
        )
        self.assertEqual(ledger["adjusted_amount"], 132.0)
        self.assertEqual(ledger["charity_allocation"], 1.32)
        self.assertEqual(ledger["settlement_amount"], 130.68)
        with self.assertRaises(ValueError):
            process_financial_simulation(FinancialTransactionConfig(-1, 0, 0))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "transactions.sqlite3"
        self.previous_database = os.environ.get("ELM369_DB_PATH")
        os.environ["ELM369_DB_PATH"] = str(self.database)
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        if self.previous_database is None:
            os.environ.pop("ELM369_DB_PATH", None)
        else:
            os.environ["ELM369_DB_PATH"] = self.previous_database
        self.temp_dir.cleanup()

    def test_health_and_influence_endpoints(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertIn("JMR08241978202646902", health.json()["identifiers"])

        influence = self.client.post(
            "/influence",
            json={"reach": 10, "viral_velocity": 2, "sentiment_delta": 0.5},
        )
        self.assertEqual(influence.status_code, 200)
        self.assertEqual(influence.json()["influence_weight"], 30)

    def test_logistics_unknown_node_returns_client_error(self):
        response = self.client.post(
            "/logistics", json={"origin": "Unknown", "destination": "Kokomo"}
        )
        self.assertEqual(response.status_code, 400)

    def test_transaction_persists_and_metrics_are_scrapeable(self):
        response = self.client.post(
            "/transaction",
            json={
                "base_amount": 100,
                "supply_volatility": 0.1,
                "demand_flux": 0.2,
            },
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["ledger"]["charity_allocation"], 1.32)
        self.assertGreater(result["transaction_id"], 0)

        with sqlite3.connect(self.database) as connection:
            rows = connection.execute(
                "SELECT ledger_json FROM transactions"
            ).fetchall()
        self.assertEqual(json.loads(rows[0][0]), result["ledger"])

        metrics = self.client.get("/metrics")
        self.assertEqual(metrics.status_code, 200)
        self.assertIn('path="/transaction"', metrics.text)
        self.assertIn("elm369_http_requests_total", metrics.text)

    def test_invalid_input_is_rejected(self):
        response = self.client.post(
            "/influence",
            json={"reach": -1, "viral_velocity": 2, "sentiment_delta": 0},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
