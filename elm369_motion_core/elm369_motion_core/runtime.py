"""Deterministic fixed-step motion-state runtime and replayable event log."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from math import isfinite
from .quaternion import Quaternion


@dataclass(frozen=True)
class MotionState:
    tick: int = 0
    orientation: Quaternion = Quaternion()
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)


class DeterministicMotionRuntime:
    """Pure-Python simulation core; no hardware access or wall-clock reads."""
    def __init__(self, *, fixed_dt: float = 1.0 / 60.0,
                 initial: MotionState | None = None) -> None:
        if not isfinite(fixed_dt) or fixed_dt <= 0:
            raise ValueError("fixed_dt must be finite and greater than zero.")
        self.fixed_dt = fixed_dt
        self.state = initial or MotionState()
        self.events: list[dict[str, object]] = []

    def step(self, angular_velocity: tuple[float, float, float],
             linear_velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
             ) -> MotionState:
        if len(angular_velocity) != 3 or len(linear_velocity) != 3:
            raise ValueError("Angular and linear velocity must be 3-vectors.")
        values = tuple(float(v) for v in (*angular_velocity, *linear_velocity))
        if not all(isfinite(v) for v in values):
            raise ValueError("Motion inputs must be finite.")
        wx, wy, wz, vx, vy, vz = values
        old = self.state
        orientation = old.orientation.integrate(wx, wy, wz, self.fixed_dt)
        position = tuple(old.position[i] + values[i+3] * self.fixed_dt
                         for i in range(3))
        self.state = MotionState(old.tick + 1, orientation, position)
        self.events.append({
            "tick": self.state.tick,
            "dt": self.fixed_dt,
            "angular_velocity": [wx, wy, wz],
            "linear_velocity": [vx, vy, vz],
            "orientation": [orientation.w, orientation.x, orientation.y, orientation.z],
            "position": list(position),
        })
        return self.state

    def replay_hash(self) -> str:
        """Stable SHA-256 digest of the ordered event log."""
        payload = json.dumps(self.events, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")
        return sha256(payload).hexdigest()
