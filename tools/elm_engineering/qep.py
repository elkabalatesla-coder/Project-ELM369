"""Offline Quality/Efficiency/Productivity planning profiles, not machine control."""

import argparse
import json

from .engine import ELM369EngineeringCore, _require_finite


class ELM369QEPShuffler:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def shuffle_pyramid_focus(self, demand_focus: str):
        """Select a fresh planning profile without changing operational state."""
        if not isinstance(demand_focus, str):
            raise ValueError("demand_focus must be a string.")
        focus_normalized = demand_focus.strip().upper()
        pyramid_modes = {
            "QUALITY": {
                "priority_tier": "QUALITY-CENTRIC (Mode 1)",
                "foundation": "Absolute Metrology, GD&T, & Poka-Yoke Interlocks",
                "core_mechanism": "In-Situ SPC Monitoring & HITL Validation",
                "apex_target": "Zero-Defect Delivery & Precision Compliance",
                "resource_weight": {"quality": 0.60, "efficiency": 0.20, "productivity": 0.20},
            },
            "PRODUCTIVITY": {
                "priority_tier": "PRODUCTIVITY-CENTRIC (Mode 2)",
                "foundation": "Rapid Deployment & Quick-Change Setup",
                "core_mechanism": "Fleet Uptime & High-Speed Cycle Synchronization",
                "apex_target": "Maximum Output Volume & Throughput",
                "resource_weight": {"quality": 0.20, "efficiency": 0.20, "productivity": 0.60},
            },
            "EFFICIENCY": {
                "priority_tier": "EFFICIENCY-CENTRIC (Mode 3)",
                "foundation": "Live Telemetry & Energy/Resource Auditing",
                "core_mechanism": "Dynamic Feed/Speed Tuning & Lean Flow",
                "apex_target": "Zero Waste & Maximum Resource ROI",
                "resource_weight": {"quality": 0.25, "efficiency": 0.50, "productivity": 0.25},
            },
        }
        if focus_normalized not in pyramid_modes:
            return {
                "error": f"Invalid demand focus '{demand_focus}'. Choose QUALITY, PRODUCTIVITY, or EFFICIENCY."
            }
        return {
            "project_id": self.project_id,
            "companion_id": self.companion_id,
            "selected_focus": focus_normalized,
            "pyramid_structure": pyramid_modes[focus_normalized],
            "execution_mode": "PLANNING_ONLY",
            "executed": False,
            "limitations": (
                "Profile descriptions are proposed practices and targets, not active telemetry, "
                "interlocks, SPC, HITL verification, tuning, or verified performance. "
                "Weights are planning preferences, never permission to relax safety requirements."
            ),
            "governance_audit": self.apply_governance_audit(),
        }

    def apply_governance_audit(self):
        """Return a fixed 1% baseline simulation without pool logging or payments."""
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        allocation = ELM369EngineeringCore(self.project_id).evaluate_project_resource_allocation(10000.0)
        return {
            "simulation_only": True,
            "simulated_value": allocation["gross_value"],
            "purple_pool_status": "ACTIVE",
            "purple_pool_logged": False,
            "charity_fee_1_percent": allocation["charity_allocation"],
            "charity_targets": allocation["charity_targets"],
            "net_operational_resource": allocation["net_retained_resource"],
            "funds_transferred": False,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description="ELM369 QEP planning profile selection; no operational execution.")
    parser.add_argument("focus", nargs="?", default="QUALITY", help="QUALITY, PRODUCTIVITY, or EFFICIENCY.")
    args = parser.parse_args(argv)
    result = ELM369QEPShuffler().shuffle_pyramid_focus(args.focus)
    print("=== PROJECT ELM369: QEP PLANNING ONLY - NO OPERATIONAL EXECUTION ===")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    raise SystemExit(main())
