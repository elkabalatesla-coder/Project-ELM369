"""Offline energy and material conservation estimates; no equipment control."""

import json
from fractions import Fraction

from .engine import ELM369EngineeringCore, _require_finite


def _nonnegative(**values):
    _require_finite(**values)
    for name, value in values.items():
        if value < 0:
            raise ValueError(f"{name} must be nonnegative.")


def _reported(value):
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("Estimate exceeds floating-point output range.") from exc
    _require_finite(estimate=result)
    if value != 0 and result == 0:
        raise ValueError("Estimate is below floating-point output resolution.")
    return round(result, 2)


class ELM369EfficiencyEngine:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def optimize_energy_and_power_consumption(
        self, base_power_kw: float, optimized_power_kw: float,
        operating_hours: int, cost_per_kwh: float,
    ):
        """Compare constant-power scenarios; calculate savings, not investment ROI."""
        _nonnegative(
            base_power_kw=base_power_kw, optimized_power_kw=optimized_power_kw,
            operating_hours=operating_hours, cost_per_kwh=cost_per_kwh,
        )
        if base_power_kw == 0:
            raise ValueError("base_power_kw must be positive for a reduction percentage.")
        base, proposed, hours, tariff = (
            Fraction(str(value))
            for value in (base_power_kw, optimized_power_kw, operating_hours, cost_per_kwh)
        )
        reduction = base - proposed
        percent = _reported(reduction / base * 100)
        energy = reduction * hours
        return {
            "power_reduction_kw": _reported(reduction),
            "efficiency_gain_percentage": f"{percent}%",
            "power_reduction_percentage": percent,
            "total_energy_saved_kwh": _reported(energy),
            "financial_savings_usd": _reported(energy * tariff),
            "status": "RESOURCE_CONSERVATION_ESTIMATE_ONLY",
            "simulation_only": True,
            "optimized": False,
            "roi_calculated": False,
        }

    def execute_material_waste_audit(
        self, gross_material_weight_lbs: float, net_part_weight_lbs: float,
    ):
        """Estimate non-part material mass; its disposal or recycling is unknown."""
        _nonnegative(
            gross_material_weight_lbs=gross_material_weight_lbs,
            net_part_weight_lbs=net_part_weight_lbs,
        )
        if gross_material_weight_lbs == 0:
            raise ValueError("gross_material_weight_lbs must be positive for material yield.")
        if net_part_weight_lbs > gross_material_weight_lbs:
            raise ValueError("net_part_weight_lbs must not exceed gross input.")
        gross, net = (
            Fraction(str(value))
            for value in (gross_material_weight_lbs, net_part_weight_lbs)
        )
        percent = _reported(net / gross * 100)
        return {
            "gross_input_lbs": gross_material_weight_lbs,
            "net_output_lbs": net_part_weight_lbs,
            "scrap_waste_lbs": _reported(gross - net),
            "material_efficiency": f"{percent}%",
            "material_efficiency_percentage": percent,
            "status": "MATERIAL_YIELD_ESTIMATE_ONLY",
            "simulation_only": True,
            "governance_audit": self.apply_governance_audit(),
        }

    def apply_governance_audit(self):
        """Use the independent 8500-unit savings simulation, not measured savings."""
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        allocation = ELM369EngineeringCore(self.project_id).evaluate_project_resource_allocation(8500.0)
        return {
            "simulation_only": True,
            "simulated_savings_value": allocation["gross_value"],
            "purple_pool_status": "PRIORITIZED",
            "purple_pool_logged": False,
            "charity_fee_1_percent": allocation["charity_allocation"],
            "charity_targets": allocation["charity_targets"],
            "net_retained_efficiency_value": allocation["net_retained_resource"],
            "funds_transferred": False,
        }


def main():
    engine = ELM369EfficiencyEngine()
    energy = engine.optimize_energy_and_power_consumption(45.0, 34.0, 200, 0.12)
    waste = engine.execute_material_waste_audit(50.0, 38.0)
    print("=== PROJECT ELM369: OFFLINE EFFICIENCY ESTIMATES - NO EQUIPMENT CONTROL ===")
    print(json.dumps(energy, indent=2, allow_nan=False))
    print("\nMaterial yield & simulated governance - no funds transferred:")
    print(json.dumps(waste, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
