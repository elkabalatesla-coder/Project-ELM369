"""Academic engineering simulations for Project ELM369."""

from .engine import ELM369EngineeringCore

__all__ = [
    "ELM369EngineeringCore", "ELM369CNCExecutionEngine",
    "ELM369DynamicEngine", "ELM369QEPShuffler",
    "ELM369QualityInspectionEngine",
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
