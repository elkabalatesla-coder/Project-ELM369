import contextlib
import io
import json
import math
import unittest
from unittest.mock import patch

from tools.elm_engineering import ELM369QEPShuffler
from tools.elm_engineering.qep import main


class QEPTests(unittest.TestCase):
    def setUp(self):
        self.shuffler = ELM369QEPShuffler()

    def test_profiles_and_normalization(self):
        expected = {
            "QUALITY": ("QUALITY-CENTRIC (Mode 1)", (0.60, 0.20, 0.20)),
            "PRODUCTIVITY": ("PRODUCTIVITY-CENTRIC (Mode 2)", (0.20, 0.20, 0.60)),
            "EFFICIENCY": ("EFFICIENCY-CENTRIC (Mode 3)", (0.25, 0.50, 0.25)),
        }
        for focus, (tier, weights) in expected.items():
            for text in [focus, f" \t{focus.lower()}\n"]:
                with self.subTest(text=text):
                    result = self.shuffler.shuffle_pyramid_focus(text)
                    self.assertEqual(result["selected_focus"], focus)
                    profile = result["pyramid_structure"]
                    self.assertEqual(profile["priority_tier"], tier)
                    actual = profile["resource_weight"]
                    self.assertEqual(actual, dict(zip(
                        ("quality", "efficiency", "productivity"), weights
                    )))
                    self.assertAlmostEqual(math.fsum(actual.values()), 1)
                    self.assertTrue(all(0 <= value <= 1 for value in actual.values()))
                    for field in ["foundation", "core_mechanism", "apex_target"]:
                        self.assertTrue(profile[field])
                    self.assertEqual(result["execution_mode"], "PLANNING_ONLY")
                    self.assertFalse(result["executed"])
                    self.assertIn("never permission to relax safety", result["limitations"])

    def test_invalid_focus_has_no_fallback_or_audit(self):
        with patch.object(self.shuffler, "apply_governance_audit") as audit:
            for focus in ["", " \t\n", "UNKNOWN", "CNC", "QUALITY;EFFICIENCY"]:
                result = self.shuffler.shuffle_pyramid_focus(focus)
                self.assertEqual(set(result), {"error"})
                self.assertIn("Choose QUALITY, PRODUCTIVITY, or EFFICIENCY", result["error"])
        audit.assert_not_called()

    def test_non_string_inputs(self):
        for value in [None, True, 1, [], {}, b"QUALITY"]:
            with self.assertRaises(ValueError):
                self.shuffler.shuffle_pyramid_focus(value)

    def test_governance_and_identifiers(self):
        result = self.shuffler.shuffle_pyramid_focus("QUALITY")
        self.assertEqual(result["project_id"], "JMR0824197846902")
        self.assertEqual(result["companion_id"], "JMR08241978202646902")
        self.assertEqual(ELM369QEPShuffler("custom").project_id, "custom")
        audit = result["governance_audit"]
        self.assertEqual(audit["simulated_value"], 10000)
        self.assertEqual(audit["charity_fee_1_percent"], 100)
        self.assertEqual(audit["net_operational_resource"], 9900)
        self.assertEqual(audit["charity_targets"], [
            "Shriners", "Cancer/Stroke Research", "Human Trafficking Prevention"
        ])
        self.assertEqual(audit["purple_pool_status"], "ACTIVE")
        self.assertTrue(audit["simulation_only"])
        self.assertFalse(audit["purple_pool_logged"])
        self.assertFalse(audit["funds_transferred"])

    def test_fixed_rate(self):
        for rate in [0, -0.01, 0.02, math.nan, math.inf, -math.inf, True, "0.01"]:
            self.shuffler.charity_fee_rate = rate
            with self.assertRaises(ValueError):
                self.shuffler.apply_governance_audit()
            with self.assertRaises(ValueError):
                self.shuffler.shuffle_pyramid_focus("QUALITY")

    def test_results_are_independent(self):
        first = self.shuffler.shuffle_pyramid_focus("QUALITY")
        first["pyramid_structure"]["resource_weight"]["quality"] = 0
        first["pyramid_structure"]["foundation"] = "changed"
        first["governance_audit"]["charity_targets"].clear()
        self.shuffler.shuffle_pyramid_focus("EFFICIENCY")
        second = self.shuffler.shuffle_pyramid_focus("QUALITY")
        self.assertEqual(second["pyramid_structure"]["resource_weight"]["quality"], 0.60)
        self.assertNotEqual(second["pyramid_structure"]["foundation"], "changed")
        self.assertEqual(len(second["governance_audit"]["charity_targets"]), 3)

    def test_no_network_or_domain_execution(self):
        with patch("socket.socket", side_effect=AssertionError("No network")), patch(
            "tools.elm_engineering.cnc.ELM369CNCExecutionEngine.generate_validated_gcode",
            side_effect=AssertionError("No implicit CNC execution"),
        ):
            for focus in ["QUALITY", "PRODUCTIVITY", "EFFICIENCY"]:
                self.assertFalse(self.shuffler.shuffle_pyramid_focus(focus)["executed"])

    def test_cli_modes_default_and_errors(self):
        for args, focus in [
            ([], "QUALITY"), ([" quality "], "QUALITY"),
            (["PRODUCTIVITY"], "PRODUCTIVITY"), (["efficiency"], "EFFICIENCY"),
            (["unknown"], None), ([""], None),
        ]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(args), 0 if focus else 1)
            header, payload = output.getvalue().split("\n", 1)
            self.assertIn("NO OPERATIONAL EXECUTION", header)
            result = json.loads(payload)
            if focus:
                self.assertEqual(result["selected_focus"], focus)
            else:
                self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
