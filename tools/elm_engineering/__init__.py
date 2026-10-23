"""Academic engineering simulations for Project ELM369."""

from .engine import ELM369EngineeringCore

__all__ = [
    "ELM369EngineeringCore", "ELM369CNCExecutionEngine",
    "ELM369DynamicEngine", "ELM369QEPShuffler",
    "ELM369QualityInspectionEngine",
    "ELM369ProductivityEngine",
    "ELM369EfficiencyEngine",
    "ELM369MasterSimulation",
]


def __getattr__(name):
    if name == "ELM369CNCExecutionEngine":
        from .cnc import ELM369CNCExecutionEngine

        return ELM369CNCExecutionEngine
    if name == "ELM369DynamicEngine":
        from .dynamic import ELM369DynamicEngine

        return ELM369DynamicEngine
    if name == "ELM369QEPShuffler":
        from .qep import ELM369QEPShuffler

        return ELM369QEPShuffler
    if name == "ELM369QualityInspectionEngine":
        from .quality import ELM369QualityInspectionEngine

        return ELM369QualityInspectionEngine
    if name == "ELM369ProductivityEngine":
        from .productivity import ELM369ProductivityEngine

        return ELM369ProductivityEngine
    if name == "ELM369EfficiencyEngine":
        from .efficiency import ELM369EfficiencyEngine

        return ELM369EfficiencyEngine
    if name == "ELM369MasterSimulation":
        from .master import ELM369MasterSimulation

        return ELM369MasterSimulation
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
