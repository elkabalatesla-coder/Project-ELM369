import contextlib
import io
import math
import unittest
from unittest.mock import patch

from tools.elm_engineering import ELM369ProductivityEngine
from tools.elm_engineering.productivity import main


class ProductivityTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369ProductivityEngine()

    def test_example_and_unrounded_throughput(self):
        result = self.engine.maximize_throughput_metrics(500, 4.5, 1.5)
        self.assertEqual(result["estimated_production_hours"], 39)
        self.assertEqual(result["throughput_parts_per_hour"], 12.82)
        self.assertFalse(result["optimized"])
        self.assertTrue(result["simulation_only"])
        result = self.engine.maximize_throughput_metrics(1, 1, 0)
        self.assertEqual(result["throughput_parts_per_hour"], 60)
        self.assertEqual(result["unrounded_production_hours"], 1 / 60)

    def test_empty_batches(self):
        for setup in [0, 1.5]:
            result = self.engine.maximize_throughput_metrics(0, 4.5, setup)
            self.assertEqual(result["estimated_production_hours"], setup)
            self.assertEqual(result["throughput_parts_per_hour"], 0)

    def test_invalid_throughput_inputs(self):
        for index in range(3):
            for invalid in [math.nan, math.inf, -math.inf, True, None, "1", -1, 10**1000]:
                args = [500, 4.5, 1.5]
                args[index] = invalid
                with self.subTest(index=index, invalid=str(invalid)):
                    with self.assertRaises(ValueError):
                        self.engine.maximize_throughput_metrics(*args)
        for args in [(1.5, 4.5, 1.5), (1, 0, 0)]:
            with self.assertRaises(ValueError):
                self.engine.maximize_throughput_metrics(*args)

    def test_extreme_results(self):
        for args in [(120, 1e308, 1e308), (1, 1e-308, 0)]:
            with self.assertRaises(ValueError):
                self.engine.maximize_throughput_metrics(*args)
        result = self.engine.maximize_throughput_metrics(60, 1e308, 0)
        self.assertEqual(result["unrounded_production_hours"], 1e308)

    def test_fleet_example_and_boundaries(self):
        for units, uptime, equivalent, whole in [
            (12, 95.0, 11.4, 11), (0, 95, 0, 0),
            (12, 0, 0, 0), (12, 100, 12, 12), (100, 29, 29, 29),
        ]:
            result = self.engine.execute_fleet_synchronization(units, uptime)
            self.assertEqual(result["expected_available_unit_equivalents"], equivalent)
            self.assertEqual(result["effective_synchronized_fleet"], whole)
            self.assertEqual(result["operational_uptime_percentage"], uptime)
            self.assertFalse(result["synchronization_executed"])
            self.assertEqual(result["fleet_status"], "AVAILABILITY_ESTIMATE_ONLY")

    def test_invalid_fleet_inputs(self):
        for value in [-1, 1.5, True, math.nan, math.inf, None, "12", 10**1000]:
            with self.assertRaises(ValueError):
                self.engine.execute_fleet_synchronization(value, 95)
        for value in [-0.1, 100.1, True, math.nan, math.inf, -math.inf, None, "95"]:
            with self.assertRaises(ValueError):
                self.engine.execute_fleet_synchronization(12, value)

    def test_governance_and_ids(self):
        self.assertEqual(self.engine.project_id, "JMR0824197846902")
        self.assertEqual(self.engine.companion_id, "JMR08241978202646902")
        audit = self.engine.apply_governance_audit()
        self.assertEqual(audit["simulated_value"], 25000)
        self.assertEqual(audit["charity_fee_1_percent"], 250)
        self.assertEqual(audit["net_retained_productivity_value"], 24750)
        self.assertEqual(audit["charity_targets"], [
            "Shriners", "Cancer/Stroke Research", "Human Trafficking Prevention"
        ])
        self.assertFalse(audit["purple_pool_logged"])
        self.assertFalse(audit["funds_transferred"])
        for rate in [0, 0.02, True, math.nan, math.inf, "0.01"]:
            self.engine.charity_fee_rate = rate
            with self.assertRaises(ValueError):
                self.engine.apply_governance_audit()

    def test_no_network_and_demo(self):
        output = io.StringIO()
        with patch("socket.socket", side_effect=AssertionError("No network")), contextlib.redirect_stdout(output):
            main()
        self.assertIn("12.82", output.getvalue())
        self.assertIn("11.4", output.getvalue())
        self.assertIn("NO FLEET CONTROL", output.getvalue())
        self.assertNotIn("THROUGHPUT_MAXIMIZED_VELOCITY_ACTIVE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
