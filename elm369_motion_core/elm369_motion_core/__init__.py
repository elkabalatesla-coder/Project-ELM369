"""ELM369 deterministic motion and decision core.

This package uses classical mathematics. QBIT-inspired scoring is not quantum
computation and does not claim quantum advantage.
"""
from .matrix import Matrix4, transform_point
from .quaternion import Quaternion
from .scoring import DecisionInputs, DecisionResult, score_action
from .runtime import MotionState, DeterministicMotionRuntime

__all__ = [
    "Matrix4", "transform_point", "Quaternion",
    "DecisionInputs", "DecisionResult", "score_action",
    "MotionState", "DeterministicMotionRuntime",
]
