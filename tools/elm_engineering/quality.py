"""Offline scalar dimensional checks and unverified human review declarations."""

import json
from datetime import datetime, timezone
from fractions import Fraction

from .engine import ELM369EngineeringCore, _require_finite


class ELM369QualityInspectionEngine:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def audit_dimensional_tolerances(
        self, nominal_dimension: float, measured_dimension: float,
        upper_tolerance: float, lower_tolerance: float,
    ):
        """Compare decimal-string values exactly; all dimensions must share a unit."""
        _require_finite(
            nominal_dimension=nominal_dimension, measured_dimension=measured_dimension,
            upper_tolerance=upper_tolerance, lower_tolerance=lower_tolerance,
        )
        if lower_tolerance > upper_tolerance:
            raise ValueError("lower_tolerance must not exceed upper_tolerance.")
        deviation = Fraction(str(measured_dimension)) - Fraction(str(nominal_dimension))
        within = Fraction(str(lower_tolerance)) <= deviation <= Fraction(str(upper_tolerance))
        try:
            numeric_deviation = float(deviation)
        except OverflowError as exc:
            raise ValueError("Deviation exceeds floating-point output range.") from exc
        _require_finite(deviation=numeric_deviation)
        return {
            "nominal": nominal_dimension,
            "measured": measured_dimension,
            "deviation": numeric_deviation,
            "display_deviation": round(numeric_deviation, 5),
            "allowable_limits": [lower_tolerance, upper_tolerance],
            "within_tolerance": within,
            "inspection_result": (
                "PASS - DIMENSION WITHIN SPECIFIED LIMITS"
                if within else "FAIL - OUT OF TOLERANCE (REJECT)"
            ),
            "comparison_basis": "Exact decimal-string inputs; inclusive bounds; no pre-comparison rounding.",
            "simulation_only": True,
        }

    def execute_hitl_validation_gate(
        self, inspector_id: str, inspection_report: dict, *, human_approved: bool = False,
    ):
        """Record a caller declaration, not authenticated sign-off or production release."""
        if not isinstance(inspector_id, str) or not inspector_id.strip():
            raise ValueError("inspector_id must be a nonempty string.")
        if type(human_approved) is not bool:
            raise ValueError("human_approved must be a boolean.")
        if not isinstance(inspection_report, dict):
            raise ValueError("inspection_report must be a dimensional inspection dictionary.")
        try:
            limits = inspection_report["allowable_limits"]
            if not isinstance(limits, (list, tuple)) or len(limits) != 2:
                raise ValueError("allowable_limits must contain lower and upper tolerance.")
            verified = self.audit_dimensional_tolerances(
                inspection_report["nominal"], inspection_report["measured"],
                limits[1], limits[0],
            )
        except KeyError as exc:
            raise ValueError("Inspection report is missing required dimensional inputs.") from exc
        # Never trust a supplied PASS label as evidence of conformance.
        if not verified["within_tolerance"]:
            status = "HOLD_REQUIRES_REWORK_OR_SCRAP"
        elif human_approved:
            status = "HUMAN_APPROVAL_DECLARED_UNVERIFIED"
        else:
            status = "PENDING_HUMAN_REVIEW"
        return {
            "hitl_inspector": inspector_id.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_status": status,
            "human_approval_declared": human_approved,
            "inspector_authenticated": False,
            "production_release_authorized": False,
            "inspection_report": verified,
            "simulation_only": True,
            "governance_audit": self.apply_governance_audit(),
        }

    def apply_governance_audit(self):
        """Return the 15000-unit allocation simulation; no logging or funds transfer."""
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        allocation = ELM369EngineeringCore(self.project_id).evaluate_project_resource_allocation(15000.0)
        return {
            "simulation_only": True,
            "simulated_value": allocation["gross_value"],
            "purple_pool_status": "PRIORITIZED",
            "purple_pool_logged": False,
            "charity_fee_1_percent": allocation["charity_allocation"],
            "charity_targets": allocation["charity_targets"],
            "net_retained_value": allocation["net_retained_resource"],
            "funds_transferred": False,
        }


def main():
    engine = ELM369QualityInspectionEngine()
    report = engine.audit_dimensional_tolerances(2.000, 2.0004, 0.001, -0.001)
    gate = engine.execute_hitl_validation_gate("DEMO_INSPECTOR_NOT_AUTHENTICATED", report)
    print("=== PROJECT ELM369: OFFLINE DIMENSIONAL INSPECTION - NOT PRODUCTION RELEASE ===")
    print(json.dumps(report, indent=2, allow_nan=False))
    print("\nHuman review pending; no sign-off inferred:")
    print(json.dumps(gate, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
