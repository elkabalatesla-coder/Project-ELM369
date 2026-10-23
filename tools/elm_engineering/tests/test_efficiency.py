import contextlib
import io
import math
import unittest
from unittest.mock import patch

from tools.elm_engineering import ELM369EfficiencyEngine
from tools.elm_engineering.efficiency import main


class EfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369EfficiencyEngine()

    def test_energy_example(self):
        result = self.engine.optimize_energy_and_power_consumption(45, 34, 200, 0.12)
        self.assertEqual(result["power_reduction_kw"], 11)
        self.assertEqual(result["power_reduction_percentage"], 24.44)
        self.assertEqual(result["efficiency_gain_percentage"], "24.44%")
        self.assertEqual(result["total_energy_saved_kwh"], 2200)
        self.assertEqual(result["financial_savings_usd"], 264)
        self.assertTrue(result["simulation_only"])
        self.assertFalse(result["optimized"])
        self.assertFalse(result["roi_calculated"])

    def test_increased_power_zero_savings_and_fractional_hours(self):
        result = self.engine.optimize_energy_and_power_consumption(10, 12, 0.5, 0.1)
        self.assertEqual(result["power_reduction_percentage"], -20)
        self.assertEqual(result["total_energy_saved_kwh"], -1)
        self.assertEqual(result["financial_savings_usd"], -0.1)
        for args in [(10, 10, 20, 0.1), (10, 0, 0, 0.1), (10, 0, 20, 0)]:
            self.assertEqual(
                self.engine.optimize_energy_and_power_consumption(*args)["financial_savings_usd"], 0
            )

    def test_no_intermediate_rounding(self):
        result = self.engine.optimize_energy_and_power_consumption(1, 0.999, 1000, 0.2)
        self.assertEqual(result["power_reduction_kw"], 0)
        self.assertEqual(result["total_energy_saved_kwh"], 1)
        self.assertEqual(result["financial_savings_usd"], 0.2)

    def test_invalid_energy_inputs(self):
        for index in range(4):
            for value in [-1, math.nan, math.inf, -math.inf, True, None, "1", 10**1000]:
                args = [45, 34, 200, 0.12]
                args[index] = value
                with self.subTest(index=index, invalid=str(value)):
                    with self.assertRaises(ValueError):
                        self.engine.optimize_energy_and_power_consumption(*args)
        for args in [(0, 0, 200, 0.12), (1e308, 0, 1e308, 1)]:
            with self.assertRaises(ValueError):
                self.engine.optimize_energy_and_power_consumption(*args)

    def test_material_example_and_boundaries(self):
        for gross, net, scrap, yield_pct in [
            (50, 38, 12, 76), (50, 0, 50, 0), (50, 50, 0, 100),
            (0.3, 0.2, 0.1, 66.67),
        ]:
            result = self.engine.execute_material_waste_audit(gross, net)
            self.assertEqual(result["scrap_waste_lbs"], scrap)
            self.assertEqual(result["material_efficiency_percentage"], yield_pct)
            self.assertEqual(result["material_efficiency"], f"{float(yield_pct)}%")

    def test_invalid_material_inputs(self):
        for index in range(2):
            for value in [-1, math.nan, math.inf, -math.inf, True, None, "1"]:
                args = [50, 38]
                args[index] = value
                with self.assertRaises(ValueError):
                    self.engine.execute_material_waste_audit(*args)
        for args in [(0, 0), (10, 11)]:
            with self.assertRaises(ValueError):
                self.engine.execute_material_waste_audit(*args)

    def test_governance_and_ids(self):
        self.assertEqual(self.engine.project_id, "JMR0824197846902")
        self.assertEqual(self.engine.companion_id, "JMR08241978202646902")
        audit = self.engine.apply_governance_audit()
        self.assertEqual(audit["simulated_savings_value"], 8500)
        self.assertEqual(audit["charity_fee_1_percent"], 85)
        self.assertEqual(audit["net_retained_efficiency_value"], 8415)
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
        self.assertIn("2200.0", output.getvalue())
        self.assertIn("264.0", output.getvalue())
        self.assertIn("NO EQUIPMENT CONTROL", output.getvalue())
        self.assertNotIn('"RESOURCE_CONSERVATION_OPTIMIZED"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
