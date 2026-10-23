import contextlib
import io
import math
import unittest
from unittest.mock import patch

from tools.elm_engineering import ELM369CNCExecutionEngine
from tools.elm_engineering.cnc import main


class CNCTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369CNCExecutionEngine()

    def test_parameters_and_assumptions(self):
        result = self.engine.calculate_optimal_machining_parameters(250, 0.5, 300, 0.0025, 4)
        self.assertEqual(result["spindle_speed_rpm"], 2292.0)
        self.assertEqual(result["feed_rate_ipm"], 22.92)
        self.assertEqual(result["material_removal_rate_in3_min"], 0.2865)
        self.assertEqual(result["validation_status"], "ESTIMATE_ONLY_NOT_MACHINE_VALIDATED")
        self.assertEqual(result["assumptions"]["material_hardness_brinell"], 250)
        self.assertEqual(result["assumptions"]["axial_depth_in"], 0.05)
        self.assertEqual(result["assumptions"]["radial_width_in"], 0.25)
        self.assertTrue(result["warnings"])

    def test_no_intermediate_rounding(self):
        result = self.engine.calculate_optimal_machining_parameters(250, 0.7, 301, 0.012345, 7)
        rpm = 301 * 3.82 / 0.7
        feed = rpm * 7 * 0.012345
        self.assertEqual(result["feed_rate_ipm"], round(feed, 2))
        self.assertEqual(result["material_removal_rate_in3_min"], round(feed * 0.05 * 0.35, 4))

    def test_invalid_machining_inputs(self):
        for index in range(5):
            for invalid in [0, -1, math.nan, math.inf, -math.inf, True, "1", 10**1000]:
                args = [250, 0.5, 300, 0.0025, 4]
                args[index] = invalid
                with self.subTest(index=index, invalid=str(invalid)):
                    with self.assertRaises(ValueError):
                        self.engine.calculate_optimal_machining_parameters(*args)
        with self.assertRaises(ValueError):
            self.engine.calculate_optimal_machining_parameters(250, 0.5, 300, 0.0025, 2.5)

    def test_unrepresentable_estimates(self):
        for args in [
            (250, 1e-300, 1e308, 0.01, 4),
            (250, 0.5, 300, 1e-300, 4),
            (250, 1e308, 1e-300, 0.01, 4),
        ]:
            with self.assertRaises(ValueError):
                self.engine.calculate_optimal_machining_parameters(*args)

    def test_preview_is_comment_only(self):
        lines = self.engine.generate_validated_gcode(1, 2292, 22.92, -0.125)
        for line in lines:
            self.assertTrue(line.startswith("(") and line.endswith(")"))
            self.assertEqual(line.count("("), 1)
            self.assertEqual(line.count(")"), 1)
            self.assertNotIn("\n", line)
        self.assertIn("(G01 Z-0.1250 F22.9200)", lines)
        self.assertIn("(G17 G20 G40 G80 G90 G94)", lines)
        self.assertIn("(T01 M06)", lines)
        self.assertIn("(S2292 M03)", lines)
        self.assertLess(lines.index("(G00 Z0.5)"), lines.index("(G00 X0.0 Y0.0)"))
        self.assertIn("DO NOT RUN", lines[0])
        self.assertTrue(any("UTC TIMESTAMP:" in line and "+00:00" in line for line in lines))

    def test_invalid_preview_inputs(self):
        for index in range(4):
            for invalid in [math.nan, math.inf, -math.inf, True, "1", 10**1000]:
                args = [1, 2292, 22.92, -0.125]
                args[index] = invalid
                with self.assertRaises(ValueError):
                    self.engine.generate_validated_gcode(*args)
        for args in [
            (0, 2292, 22.92, -0.125), (1.5, 2292, 22.92, -0.125),
            (1, 0, 22.92, -0.125), (1, 0.5, 22.92, -0.125),
            (1, 2292, -1, -0.125), (1, 2292, 0.00001, -0.125),
            (1, 2292, 22.92, 0), (1, 2292, 22.92, 1),
            (1, 2292, 22.92, -0.00001),
        ]:
            with self.assertRaises(ValueError):
                self.engine.generate_validated_gcode(*args)

    def test_identifier_injection(self):
        for value in ["", "bad)\nM03\n(", "(comment)", "a" * 65, 123, "é"]:
            with self.assertRaises(ValueError):
                ELM369CNCExecutionEngine(value)
        for attribute in ["project_id", "companion_id"]:
            engine = ELM369CNCExecutionEngine()
            setattr(engine, attribute, "bad)\nM03")
            with self.assertRaises(ValueError):
                engine.generate_validated_gcode(1, 2292, 22.92, -0.125)

    def test_governance_and_identifiers(self):
        self.assertEqual(self.engine.project_id, "JMR0824197846902")
        self.assertEqual(self.engine.companion_id, "JMR08241978202646902")
        result = self.engine.apply_governance_and_charity(5000)
        self.assertEqual(result["charity_allocation_1_percent"], 50)
        self.assertEqual(result["net_project_allocation"], 4950)
        self.assertEqual(len(result["charity_targets"]), 3)
        self.assertEqual(self.engine.apply_governance_and_charity(0)["gross_job_value"], 0)
        for value in [-1, math.nan, math.inf, True, "5000"]:
            with self.assertRaises(ValueError):
                self.engine.apply_governance_and_charity(value)
        self.engine.charity_fee_rate = 0.5
        with self.assertRaises(ValueError):
            self.engine.apply_governance_and_charity(5000)

    def test_demo_uses_calculated_parameters(self):
        with patch.object(
            ELM369CNCExecutionEngine, "calculate_optimal_machining_parameters",
            return_value={"spindle_speed_rpm": 1234, "feed_rate_ipm": 12.34},
        ), patch.object(
            ELM369CNCExecutionEngine, "generate_validated_gcode", return_value=[]
        ) as generate, contextlib.redirect_stdout(io.StringIO()):
            main()
        generate.assert_called_once_with(
            tool_number=1, rpm=1234, feed_rate=12.34, target_depth=-0.125
        )


if __name__ == "__main__":
    unittest.main()
