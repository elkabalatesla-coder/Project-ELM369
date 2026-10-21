"""ELM369 deterministic motion, camera, and decision core.

QBIT-inspired scoring uses classical mathematics; it is not quantum computation.
"""
from .matrix import Matrix4, transform_point
from .quaternion import Quaternion
from .scoring import DecisionInputs, DecisionResult, score_action
from .runtime import MotionState, DeterministicMotionRuntime
from .camera import CameraPose, CameraController
from .sensor_fusion import TiltEstimate, ComplementaryTiltFilter
from .collision import AABB
from .arcade_demo import ArcadeSnapshot, GyroArcadeDemo

__all__ = [
    "Matrix4", "transform_point", "Quaternion",
    "DecisionInputs", "DecisionResult", "score_action",
    "MotionState", "DeterministicMotionRuntime",
    "CameraPose", "CameraController", "TiltEstimate",
    "ComplementaryTiltFilter", "AABB", "ArcadeSnapshot", "GyroArcadeDemo",
]
