"""Offline CNC estimates and comment-only previews, never machine execution."""

import json
import re
from datetime import datetime, timezone

from .engine import ELM369EngineeringCore, _require_finite


def _positive(**values):
    _require_finite(**values)
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")


def _identifier(value):
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value) is None:
        raise ValueError("Project identifiers must be 1-64 ASCII letters, digits, _ or -.")
    return value


class ELM369CNCExecutionEngine:
    """Compatibility name for a planning tool, not an execution controller."""

    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = _identifier(project_id)
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def calculate_optimal_machining_parameters(
        self, material_hardness_brinell: int, tool_diameter: float,
        sfm: int, ipt: float, flutes: int,
    ):
        """Estimate RPM/IPM/MRR in inch units; no optimization or safety certification."""
        _positive(
            material_hardness_brinell=material_hardness_brinell,
            tool_diameter=tool_diameter, sfm=sfm, ipt=ipt, flutes=flutes,
        )
        if not isinstance(flutes, int):
            raise ValueError("flutes must be a positive integer.")
        rpm = sfm * 3.82 / tool_diameter
        feed = rpm * flutes * ipt
        axial_depth = 0.050
        radial_width = tool_diameter * 0.5
        mrr = feed * axial_depth * radial_width
        _positive(spindle_speed_rpm=rpm, feed_rate_ipm=feed, mrr=mrr)
        result = {
            "spindle_speed_rpm": round(rpm, 2),
            "feed_rate_ipm": round(feed, 2),
            "material_removal_rate_in3_min": round(mrr, 4),
        }
        _positive(**result)
        return {
            **result,
            "validation_status": "ESTIMATE_ONLY_NOT_MACHINE_VALIDATED",
            "assumptions": {
                "tool_diameter_unit": "inch",
                "surface_speed_unit": "feet/minute",
                "chip_load_unit": "inch/tooth",
                "axial_depth_in": axial_depth,
                "radial_width_in": radial_width,
                "material_hardness_brinell": material_hardness_brinell,
            },
            "warnings": [
                "Hardness is recorded, not used to select or validate SFM or chip load.",
                "No NIMS compliance, optimality, or safe-tolerance certification is established.",
                "MRR assumes a lateral cut; it does not describe the axial plunge preview.",
                "Machine, toolmaker, workholding, stock, and controller limits require independent review.",
            ],
        }

    def generate_validated_gcode(
        self, tool_number: int, rpm: float, feed_rate: float, target_depth: float,
    ):
        """Return comment-only G-code candidates; method name does not imply validation."""
        _positive(tool_number=tool_number, rpm=rpm, feed_rate=feed_rate)
        _require_finite(target_depth=target_depth)
        if not isinstance(tool_number, int):
            raise ValueError("tool_number must be a positive integer.")
        if target_depth >= 0:
            raise ValueError("target_depth must be negative relative to the assumed stock top.")
        spindle = int(rpm)
        feed = f"{feed_rate:.4f}"
        plunge = f"{feed_rate * 0.5:.4f}"
        depth = f"{target_depth:.4f}"
        if spindle < 1 or float(feed) <= 0 or float(plunge) <= 0 or float(depth) >= 0:
            raise ValueError("RPM, feed, or depth is below preview output resolution.")
        project_id = _identifier(self.project_id)
        companion_id = _identifier(self.companion_id)
        candidates = [
            "PROJECT ELM369 - COMMENT-ONLY CNC PREVIEW - DO NOT RUN",
            "NOT MACHINE VALIDATED - NO HARDWARE CONNECTION OR EXECUTION",
            f"SYS IDs: {project_id} / {companion_id}",
            f"UTC TIMESTAMP: {datetime.now(timezone.utc).isoformat()}",
            "Setup, offsets, tool length, travel, spindle and workholding not validated",
            "Candidate inch-unit plunge at X0 Y0; stock top assumed Z0",
            "G17 G20 G40 G80 G90 G94",
            f"T{tool_number:02d} M06",
            f"S{spindle} M03",
            "G00 Z0.5",
            "G00 X0.0 Y0.0",
            f"G01 Z0.1 F{plunge}",
            f"G01 Z{depth} F{feed}",
            "G00 Z1.0",
            "M05",
            "M30",
        ]
        return [f"({line})" for line in candidates]

    def apply_governance_and_charity(self, simulated_job_value: float):
        """Reuse the engineering simulation allocation; no funds are moved."""
        core = ELM369EngineeringCore(self.project_id)
        core.charity_fee_rate = self.charity_fee_rate
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        allocation = core.evaluate_project_resource_allocation(simulated_job_value)
        return {
            "gross_job_value": allocation["gross_value"],
            "charity_allocation_1_percent": allocation["charity_allocation"],
            "charity_targets": allocation["charity_targets"],
            "net_project_allocation": allocation["net_retained_resource"],
        }


def main():
    engine = ELM369CNCExecutionEngine()
    machining_specs = engine.calculate_optimal_machining_parameters(
        material_hardness_brinell=250, tool_diameter=0.5,
        sfm=300, ipt=0.0025, flutes=4,
    )
    gcode_program = engine.generate_validated_gcode(
        tool_number=1, rpm=machining_specs["spindle_speed_rpm"],
        feed_rate=machining_specs["feed_rate_ipm"], target_depth=-0.125,
    )
    governance_audit = engine.apply_governance_and_charity(5000.0)
    print("=== PROJECT ELM369: CNC PLANNING SIMULATION - NOT FOR MACHINE EXECUTION ===")
    print(json.dumps(machining_specs, indent=2, allow_nan=False))
    print("\nComment-only G-code preview:")
    print("\n".join(gcode_program))
    print("\nSimulated governance & charity allocation - no funds transferred:")
    print(json.dumps(governance_audit, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
