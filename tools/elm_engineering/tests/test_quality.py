import contextlib
import io
import math
import unittest
from datetime import datetime, timezone

from tools.elm_engineering import ELM369QualityInspectionEngine
from tools.elm_engineering.quality import main


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369QualityInspectionEngine()

    def report(self, measured=2.0004):
        return self.engine.audit_dimensional_tolerances(2, measured, 0.001, -0.001)

    def test_example_and_inclusive_decimal_boundaries(self):
        report = self.report()
        self.assertEqual(report["deviation"], 0.0004)
        self.assertTrue(report["within_tolerance"])
        self.assertNotIn("ZERO DEFECT", report["inspection_result"])
        for measured in [1.999, 2, 2.001]:
            self.assertTrue(self.report(measured)["within_tolerance"])

    def test_no_rounding_before_decision(self):
        for measured in [2.0010001, 1.9989999]:
            report = self.report(measured)
            self.assertFalse(report["within_tolerance"])
            self.assertEqual(abs(report["display_deviation"]), 0.001)
        self.assertTrue(self.engine.audit_dimensional_tolerances(1, 1, 0, 0)["within_tolerance"])

    def test_invalid_numeric_inputs(self):
        for index in range(4):
            for invalid in [math.nan, math.inf, -math.inf, True, None, "2", 10**1000]:
                args = [2, 2.0004, 0.001, -0.001]
                args[index] = invalid
                with self.subTest(index=index, invalid=str(invalid)):
                    with self.assertRaises(ValueError):
                        self.engine.audit_dimensional_tolerances(*args)
        with self.assertRaises(ValueError):
            self.engine.audit_dimensional_tolerances(2, 2, -0.001, 0.001)
        with self.assertRaises(ValueError):
            self.engine.audit_dimensional_tolerances(-1e308, 1e308, 1, -1)

    def test_pending_and_explicit_declaration(self):
        pending = self.engine.execute_hitl_validation_gate(" inspector ", self.report())
        self.assertEqual(pending["verification_status"], "PENDING_HUMAN_REVIEW")
        self.assertFalse(pending["human_approval_declared"])
        self.assertEqual(pending["hitl_inspector"], "inspector")
        approved = self.engine.execute_hitl_validation_gate(
            "inspector", self.report(), human_approved=True
        )
        self.assertEqual(approved["verification_status"], "HUMAN_APPROVAL_DECLARED_UNVERIFIED")
        self.assertTrue(approved["human_approval_declared"])
        for result in [pending, approved]:
            self.assertFalse(result["inspector_authenticated"])
            self.assertFalse(result["production_release_authorized"])
            self.assertEqual(datetime.fromisoformat(result["timestamp"]).utcoffset(), timezone.utc.utcoffset(None))

    def test_failed_and_forged_reports_never_approve(self):
        report = self.report(2.1)
        report["inspection_result"] = "PASS - ZERO DEFECT CONFIRMED"
        report["within_tolerance"] = True
        report["deviation"] = 0
        for approval in [False, True]:
            result = self.engine.execute_hitl_validation_gate("inspector", report, human_approved=approval)
            self.assertEqual(result["verification_status"], "HOLD_REQUIRES_REWORK_OR_SCRAP")
            self.assertFalse(result["inspection_report"]["within_tolerance"])
            self.assertFalse(result["production_release_authorized"])

    def test_malformed_gate_inputs(self):
        for inspector in ["", " \n", None, 12]:
            with self.assertRaises(ValueError):
                self.engine.execute_hitl_validation_gate(inspector, self.report())
        for approval in ["yes", 1, None, []]:
            with self.assertRaises(ValueError):
                self.engine.execute_hitl_validation_gate("inspector", self.report(), human_approved=approval)
        for report in [None, [], {}, {"inspection_result": "PASS"}]:
            with self.assertRaises(ValueError):
                self.engine.execute_hitl_validation_gate("inspector", report)
        for limits in [None, [], [1], [1, 2, 3], "12", [True, 1], [1, -1]]:
            report = {**self.report(), "allowable_limits": limits}
            with self.assertRaises(ValueError):
                self.engine.execute_hitl_validation_gate("inspector", report)

    def test_governance(self):
        self.assertEqual(self.engine.project_id, "JMR0824197846902")
        self.assertEqual(self.engine.companion_id, "JMR08241978202646902")
        audit = self.engine.apply_governance_audit()
        self.assertEqual(audit["charity_fee_1_percent"], 150)
        self.assertEqual(audit["net_retained_value"], 14850)
        self.assertEqual(audit["simulated_value"], 15000)
        self.assertEqual(len(audit["charity_targets"]), 3)
        self.assertFalse(audit["purple_pool_logged"])
        self.assertFalse(audit["funds_transferred"])
        for rate in [0.02, math.nan, True, "0.01"]:
            self.engine.charity_fee_rate = rate
            with self.assertRaises(ValueError):
                self.engine.apply_governance_audit()

    def test_demo_does_not_infer_signoff(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        self.assertIn("PENDING_HUMAN_REVIEW", output.getvalue())
        self.assertNotIn("APPROVED_BY_HUMAN_OPERATOR", output.getvalue())


if __name__ == "__main__":
    unittest.main()
