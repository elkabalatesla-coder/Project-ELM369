"""Academic engineering simulations for Project ELM369."""

from .engine import ELM369EngineeringCore

__all__ = ["ELM369EngineeringCore", "ELM369CNCExecutionEngine", "ELM369DynamicEngine"]


def __getattr__(name):
    if name == "ELM369CNCExecutionEngine":
        from .cnc import ELM369CNCExecutionEngine

        return ELM369CNCExecutionEngine
    if name == "ELM369DynamicEngine":
        from .dynamic import ELM369DynamicEngine

        return ELM369DynamicEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
