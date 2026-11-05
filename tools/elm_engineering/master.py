"""Compose offline engineering models; no operational execution or human sign-off."""

import json
from datetime import datetime, timezone

from .cnc import ELM369CNCExecutionEngine
from .efficiency import ELM369EfficiencyEngine
from .engine import ELM369EngineeringCore, _require_finite
from .productivity import ELM369ProductivityEngine
from .qep import ELM369QEPShuffler
from .quality import ELM369QualityInspectionEngine


class ELM369MasterSimulation:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.companion_id = "JMR08241978202646902"
        self.charity_fee_rate = 0.01

    def run_full_simulation(self):
        """Run the three example scenarios with explicit inputs and one aggregate baseline."""
        _require_finite(charity_fee_rate=self.charity_fee_rate)
        if self.charity_fee_rate != 0.01:
            raise ValueError("The charity allocation rate must remain 1 percent.")
        cnc = ELM369CNCExecutionEngine(self.project_id)
        quality = ELM369QualityInspectionEngine(self.project_id)
        productivity = ELM369ProductivityEngine(self.project_id)
        efficiency = ELM369EfficiencyEngine(self.project_id)
        qep = ELM369QEPShuffler(self.project_id)

        machining_inputs = {
            "material_hardness_brinell": 250, "tool_diameter": 0.5,
            "sfm": 300, "ipt": 0.0025, "flutes": 4,
        }
        machining = cnc.calculate_optimal_machining_parameters(**machining_inputs)
        inspection_inputs = {
            "nominal_dimension": 2.000, "measured_dimension": 2.0003,
            "upper_tolerance": 0.001, "lower_tolerance": -0.001,
        }
        inspection = quality.audit_dimensional_tolerances(**inspection_inputs)
        human_review = quality.execute_hitl_validation_gate(
            "DEMO_INSPECTOR_NOT_AUTHENTICATED", inspection
        )
        fleet_inputs = {"active_units": 10, "operational_uptime_percentage": 96.5}
        fleet = productivity.execute_fleet_synchronization(**fleet_inputs)
        batch_inputs = {
            "batch_size": 500, "cycle_time_minutes_per_unit": 4.5, "setup_time_hours": 1.5,
        }
        throughput = productivity.maximize_throughput_metrics(**batch_inputs)
        energy_inputs = {
            "base_power_kw": 45.0, "optimized_power_kw": 32.5,
            "operating_hours": 400, "cost_per_kwh": 0.13608,
        }
        material_inputs = {"gross_material_weight_lbs": 50.0, "net_part_weight_lbs": 41.0}
        energy = efficiency.optimize_energy_and_power_consumption(**energy_inputs)
        material = efficiency.execute_material_waste_audit(**material_inputs)
        allocation = ELM369EngineeringCore(self.project_id).evaluate_project_resource_allocation(50000.0)
        return {
            "simulation_header": {
                "system_id_primary": self.project_id,
                "system_id_companion": self.companion_id,
                "execution_timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "MASTER_SIMULATION_COMPLETED_SUCCESSFULLY",
                "execution_mode": "OFFLINE_SIMULATION_ONLY",
                "operational_execution_performed": False,
                "production_release_authorized": False,
            },
            "domain_results": [
                {
                    "domain": "Industrial & CNC Machining",
                    "demand_focus": "QUALITY (Mode 1)",
                    "qep_profile": qep.shuffle_pyramid_focus("QUALITY"),
                    "machining_inputs": machining_inputs,
                    "machining_estimate": machining,
                    "gcode_preview": cnc.generate_validated_gcode(
                        1, machining["spindle_speed_rpm"], machining["feed_rate_ipm"], -0.125
                    ),
                    "inspection_inputs": inspection_inputs,
                    "inspection_report": inspection,
                    "inspection_status": inspection["inspection_result"],
                    "hitl_review": human_review,
                },
                {
                    "domain": "Agricultural & Heavy Equipment Fleet",
                    "demand_focus": "PRODUCTIVITY (Mode 2)",
                    "qep_profile": qep.shuffle_pyramid_focus("PRODUCTIVITY"),
                    "fleet_inputs": fleet_inputs,
                    "fleet_availability": fleet,
                    "effective_synchronized_units": fleet["effective_synchronized_fleet"],
                    "batch_inputs": batch_inputs,
                    "batch_throughput": throughput,
                    "throughput_status": throughput["status"],
                    "limitations": "Generic serial-batch and equivalent-capacity models, not a field-work model or synchronized machinery.",
                },
                {
                    "domain": "Additive Manufacturing & 3D Printing",
                    "demand_focus": "EFFICIENCY (Mode 3)",
                    "qep_profile": qep.shuffle_pyramid_focus("EFFICIENCY"),
                    "energy_inputs": energy_inputs,
                    "material_inputs": material_inputs,
                    "energy_estimate": energy,
                    "material_audit": material,
                    "power_reduction_kw": energy["power_reduction_kw"],
                    "material_efficiency_pct": material["material_efficiency_percentage"],
                    "energy_savings_usd": energy["financial_savings_usd"],
                    "conservation_status": energy["status"],
                    "limitations": "Generic constant-load energy and mass-yield scenarios, not a printer physics model or verified zero waste.",
                },
            ],
            "governance_audit": {
                "simulation_only": True,
                "purple_pool_status": "ACTIVE_AND_PRIORITIZED",
                "purple_pool_logged": False,
                "gross_simulated_value_usd": allocation["gross_value"],
                "charity_allocation_1_percent": allocation["charity_allocation"],
                "charity_recipients": allocation["charity_targets"],
                "net_retained_project_resources": allocation["net_retained_resource"],
                "funds_transferred": False,
                "basis": "Independent 50000-unit scenario baseline; nested module audits are separate illustrations, not additive charges or measured economic impact. Targets are not confirmed recipients.",
            },
        }


def main():
    print(json.dumps(ELM369MasterSimulation().run_full_simulation(), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
