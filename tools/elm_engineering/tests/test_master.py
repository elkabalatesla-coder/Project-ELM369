import contextlib
import io
import json
import math
import unittest
from datetime import datetime
from unittest.mock import patch

from tools.elm_engineering import ELM369MasterSimulation
from tools.elm_engineering.master import main
from tools.elm_engineering.productivity import ELM369ProductivityEngine
from tools.elm_engineering.quality import ELM369QualityInspectionEngine


class MasterTests(unittest.TestCase):
    def test_composed_examples(self):
        result = ELM369MasterSimulation().run_full_simulation()
        self.assertEqual(len(result["domain_results"]), 3)
        cnc, agriculture, fabrication = result["domain_results"]
        self.assertTrue(cnc["inspection_report"]["within_tolerance"])
        self.assertEqual(cnc["hitl_review"]["verification_status"], "PENDING_HUMAN_REVIEW")
        self.assertFalse(cnc["hitl_review"]["production_release_authorized"])
        self.assertTrue(all(line.startswith("(") and line.endswith(")") for line in cnc["gcode_preview"]))
        self.assertEqual(agriculture["effective_synchronized_units"], 9)
        self.assertEqual(agriculture["fleet_availability"]["expected_available_unit_equivalents"], 9.65)
        self.assertEqual(agriculture["batch_throughput"]["throughput_parts_per_hour"], 12.82)
        self.assertEqual(fabrication["power_reduction_kw"], 12.5)
        self.assertEqual(fabrication["material_efficiency_pct"], 82)
        self.assertEqual(fabrication["energy_savings_usd"], 680.4)
        for domain, focus in zip(result["domain_results"], ["QUALITY", "PRODUCTIVITY", "EFFICIENCY"]):
            self.assertEqual(domain["qep_profile"]["selected_focus"], focus)
        json.dumps(result, allow_nan=False)

    def test_header_and_governance(self):
        result = ELM369MasterSimulation("CUSTOM").run_full_simulation()
        header = result["simulation_header"]
        self.assertEqual(header["system_id_primary"], "CUSTOM")
        self.assertEqual(header["system_id_companion"], "JMR08241978202646902")
        self.assertIsNotNone(datetime.fromisoformat(header["execution_timestamp"]).tzinfo)
        self.assertFalse(header["operational_execution_performed"])
        self.assertFalse(header["production_release_authorized"])
        audit = result["governance_audit"]
        self.assertEqual(audit["gross_simulated_value_usd"], 50000)
        self.assertEqual(audit["charity_allocation_1_percent"], 500)
        self.assertEqual(audit["net_retained_project_resources"], 49500)
        self.assertFalse(audit["funds_transferred"])
        self.assertFalse(audit["purple_pool_logged"])
        self.assertIn("not additive", audit["basis"])

    def test_module_outputs_not_hardcoded(self):
        report = ELM369QualityInspectionEngine().audit_dimensional_tolerances(2, 3, 0.001, -0.001)
        with patch(
            "tools.elm_engineering.master.ELM369QualityInspectionEngine.audit_dimensional_tolerances",
            return_value=report,
        ), patch(
            "tools.elm_engineering.master.ELM369ProductivityEngine.maximize_throughput_metrics",
            return_value={"status": "CUSTOM_ESTIMATE", "throughput_parts_per_hour": 7},
        ):
            result = ELM369MasterSimulation().run_full_simulation()
        self.assertEqual(result["domain_results"][0]["inspection_status"], report["inspection_result"])
        self.assertEqual(result["domain_results"][1]["throughput_status"], "CUSTOM_ESTIMATE")

    def test_errors_propagate_and_rate_fixed(self):
        with patch.object(ELM369ProductivityEngine, "execute_fleet_synchronization", side_effect=ValueError("failure")):
            with self.assertRaises(ValueError):
                ELM369MasterSimulation().run_full_simulation()
        for rate in [0.02, True, math.nan, math.inf, "0.01"]:
            engine = ELM369MasterSimulation()
            engine.charity_fee_rate = rate
            with self.assertRaises(ValueError):
                engine.run_full_simulation()

    def test_fresh_results_and_offline_demo(self):
        first = ELM369MasterSimulation().run_full_simulation()
        first["domain_results"].clear()
        output = io.StringIO()
        with patch("socket.socket", side_effect=AssertionError("No network")), contextlib.redirect_stdout(output):
            main()
        result = json.loads(output.getvalue())
        self.assertEqual(len(result["domain_results"]), 3)
        self.assertNotIn("ZERO DEFECT CONFIRMED", output.getvalue())
        self.assertNotIn("MAXIMUM FIELD VELOCITY ACHIEVED", output.getvalue())
        self.assertNotIn("ZERO WASTE LEAN FLOW ACTIVE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
