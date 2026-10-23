"""Academic engineering simulations for Project ELM369."""

from .engine import ELM369EngineeringCore

__all__ = ["ELM369EngineeringCore", "ELM369CNCExecutionEngine"]


def __getattr__(name):
    if name == "ELM369CNCExecutionEngine":
        from .cnc import ELM369CNCExecutionEngine

        return ELM369CNCExecutionEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
