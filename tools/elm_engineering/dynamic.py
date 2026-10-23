"""Defined Human Input routing metadata; does not execute domain pipelines."""

import argparse
import json

from .engine import ELM369EngineeringCore, _require_finite


class ELM369DynamicEngine:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def process_human_input_priority(self, human_choice: str):
        """Select a domain, with an explicit metadata-only CNC fallback."""
        if not isinstance(human_choice, str):
            raise ValueError("human_choice must be a string.")
        choice_normalized = human_choice.strip().upper()
        routing_table = {
            "CNC": {
                "domain": "Industrial & CNC Machining",
                "capability_status": "OFFLINE_PLANNING_AVAILABLE",
                "default_action": "Select offline SFM/IPT estimates and comment-only G-code previews for review.",
            },
            "MEDICAL": {
                "domain": "Medical & Dental Equipment",
                "capability_status": "PLANNED_NOT_IMPLEMENTED",
                "default_action": "Plan DICOM ingestion and human-in-the-loop safety review; neither is initialized.",
            },
            "AGRICULTURE": {
                "domain": "Agricultural & Heavy Machinery",
                "capability_status": "PLANNED_NOT_IMPLEMENTED",
                "default_action": "Plan CANbus J1939 telematics and hydraulic force calculations; no bus connection or calculation is started.",
            },
            "FABRICATION": {
                "domain": "Additive Manufacturing & 3D Printing",
                "capability_status": "PLANNED_NOT_IMPLEMENTED",
                "default_action": "Plan mesh parsing and in-situ layer monitoring; neither is started.",
            },
        }
        used_fallback = choice_normalized not in routing_table
        selected_priority = "CNC" if used_fallback else choice_normalized
        result = {
            "project_id": self.project_id,
            "companion_id": self.companion_id,
            "human_input_received": choice_normalized,
            "selected_priority": selected_priority,
            "used_fallback": used_fallback,
            "execution_mode": "ROUTING_ONLY",
            "executed": False,
            "routing_details": {
                **routing_table[selected_priority],
                "status": "ACTIVE_PRIMARY_VECTOR",
                "status_meaning": "Selected priority only, not an active domain pipeline.",
            },
            "governance_audit": self.apply_governance_audit(),
        }
        if used_fallback:
            result["warning"] = "Unknown or empty priority choice; selected CNC planning metadata only."
        return result

    def apply_governance_audit(self):
        """Return a baseline allocation simulation; no persistent pool logging."""
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        allocation = ELM369EngineeringCore(self.project_id).evaluate_project_resource_allocation(10000.0)
        return {
            "simulation_only": True,
            "simulated_value": allocation["gross_value"],
            "purple_pool_status": "PRIORITIZED",
            "purple_pool_logged": False,
            "charity_allocation_1_percent": allocation["charity_allocation"],
            "charity_targets": allocation["charity_targets"],
            "net_retained_allocation": allocation["net_retained_resource"],
            "funds_transferred": False,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description="ELM369 offline DHI priority selection; no domain execution.")
    parser.add_argument("priority", nargs="?", default="CNC", help="CNC, MEDICAL, AGRICULTURE, or FABRICATION; unknown choices fall back to CNC metadata.")
    args = parser.parse_args(argv)
    result = ELM369DynamicEngine().process_human_input_priority(args.priority)
    print("=== PROJECT ELM369: DHI ROUTING ONLY - NO DOMAIN EXECUTION ===")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
