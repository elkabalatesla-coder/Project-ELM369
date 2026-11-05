import contextlib
import io
import json
import math
import unittest
from unittest.mock import patch

from tools.elm_engineering import ELM369DynamicEngine
from tools.elm_engineering.dynamic import main


class DynamicTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369DynamicEngine()

    def test_all_domain_choices_and_normalization(self):
        expected = {
            "CNC": ("Industrial & CNC Machining", "OFFLINE_PLANNING_AVAILABLE"),
            "MEDICAL": ("Medical & Dental Equipment", "PLANNED_NOT_IMPLEMENTED"),
            "AGRICULTURE": ("Agricultural & Heavy Machinery", "PLANNED_NOT_IMPLEMENTED"),
            "FABRICATION": ("Additive Manufacturing & 3D Printing", "PLANNED_NOT_IMPLEMENTED"),
        }
        for choice, (domain, capability) in expected.items():
            for text in [choice, f" \t{choice.lower()}\n"]:
                with self.subTest(text=text):
                    result = self.engine.process_human_input_priority(text)
                    self.assertEqual(result["human_input_received"], choice)
                    self.assertEqual(result["selected_priority"], choice)
                    self.assertEqual(result["routing_details"]["domain"], domain)
                    self.assertEqual(result["routing_details"]["capability_status"], capability)
                    self.assertEqual(result["routing_details"]["status"], "ACTIVE_PRIMARY_VECTOR")
                    self.assertEqual(result["execution_mode"], "ROUTING_ONLY")
                    self.assertFalse(result["executed"])
                    self.assertFalse(result["used_fallback"])
                    self.assertNotIn("warning", result)

    def test_unknown_and_empty_choices_actually_select_cnc(self):
        cnc = self.engine.process_human_input_priority("CNC")
        for text in ["unknown", "", " \t\n", "MEDICAL;CNC", "<script>"]:
            result = self.engine.process_human_input_priority(text)
            self.assertEqual(result["selected_priority"], "CNC")
            self.assertEqual(result["routing_details"], cnc["routing_details"])
            self.assertEqual(result["governance_audit"], cnc["governance_audit"])
            self.assertTrue(result["used_fallback"])
            self.assertFalse(result["executed"])
            self.assertIn("warning", result)

    def test_non_string_inputs(self):
        for value in [None, True, 1, [], {}, b"CNC"]:
            with self.assertRaises(ValueError):
                self.engine.process_human_input_priority(value)

    def test_simulated_governance_and_ids(self):
        result = self.engine.process_human_input_priority("CNC")
        self.assertEqual(result["project_id"], "JMR0824197846902")
        self.assertEqual(result["companion_id"], "JMR08241978202646902")
        self.assertEqual(ELM369DynamicEngine("custom").project_id, "custom")
        audit = result["governance_audit"]
        self.assertEqual(audit["simulated_value"], 10000)
        self.assertEqual(audit["charity_allocation_1_percent"], 100)
        self.assertEqual(audit["net_retained_allocation"], 9900)
        self.assertEqual(audit["charity_targets"], [
            "Shriners", "Cancer/Stroke Research", "Human Trafficking Prevention"
        ])
        self.assertEqual(audit["purple_pool_status"], "PRIORITIZED")
        self.assertTrue(audit["simulation_only"])
        self.assertFalse(audit["purple_pool_logged"])
        self.assertFalse(audit["funds_transferred"])

    def test_fixed_rate_validation(self):
        for rate in [0, -0.01, 0.02, math.nan, math.inf, True, "0.01"]:
            self.engine.charity_fee_rate = rate
            with self.assertRaises(ValueError):
                self.engine.apply_governance_audit()
            with self.assertRaises(ValueError):
                self.engine.process_human_input_priority("CNC")

    def test_fresh_results_and_independent_calls(self):
        first = self.engine.process_human_input_priority("MEDICAL")
        first["routing_details"]["domain"] = "changed"
        first["governance_audit"]["charity_targets"].clear()
        second = self.engine.process_human_input_priority("MEDICAL")
        self.assertEqual(second["routing_details"]["domain"], "Medical & Dental Equipment")
        self.assertEqual(len(second["governance_audit"]["charity_targets"]), 3)
        self.assertEqual(self.engine.process_human_input_priority("CNC")["selected_priority"], "CNC")

    def test_no_network_or_cnc_execution(self):
        with patch("socket.socket", side_effect=AssertionError("No network")), patch(
            "tools.elm_engineering.cnc.ELM369CNCExecutionEngine.generate_validated_gcode",
            side_effect=AssertionError("No implicit CNC execution"),
        ):
            for choice in ["CNC", "MEDICAL", "AGRICULTURE", "FABRICATION", "unknown"]:
                self.assertFalse(self.engine.process_human_input_priority(choice)["executed"])

    def test_cli_default_explicit_and_fallback(self):
        for args, choice, fallback in [
            ([], "CNC", False), ([" medical "], "MEDICAL", False),
            (["agriculture"], "AGRICULTURE", False), (["FABRICATION"], "FABRICATION", False),
            (["unknown"], "CNC", True),
        ]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(args), 0)
            header, payload = output.getvalue().split("\n", 1)
            self.assertIn("NO DOMAIN EXECUTION", header)
            result = json.loads(payload)
            self.assertEqual(result["selected_priority"], choice)
            self.assertEqual(result["used_fallback"], fallback)


if __name__ == "__main__":
    unittest.main()
