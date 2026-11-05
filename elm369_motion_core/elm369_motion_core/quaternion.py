"""Quaternion orientation integration for angular-velocity samples."""
from __future__ import annotations
from dataclasses import dataclass
from math import cos, sin, sqrt, isfinite


@dataclass(frozen=True)
class Quaternion:
    """Unit quaternion in (w, x, y, z) order."""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.w, self.x, self.y, self.z)):
            raise ValueError("Quaternion components must be finite.")

    def norm(self) -> float:
        return sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)

    def normalized(self) -> "Quaternion":
        n = self.norm()
        if n <= 1e-15:
            raise ValueError("Zero quaternion cannot be normalized.")
        return Quaternion(self.w/n, self.x/n, self.y/n, self.z/n)

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w,
        )

    @classmethod
    def from_angular_velocity(cls, wx: float, wy: float, wz: float,
                              dt: float) -> "Quaternion":
        """Return delta rotation for rad/s input and nonnegative dt."""
        if not all(isfinite(v) for v in (wx, wy, wz, dt)):
            raise ValueError("Angular velocity and dt must be finite.")
        if dt < 0:
            raise ValueError("dt must be nonnegative.")
        speed = sqrt(wx*wx + wy*wy + wz*wz)
        half_angle = 0.5 * speed * dt
        if speed <= 1e-15 or dt == 0:
            return cls()
        scale = sin(half_angle) / speed
        return cls(cos(half_angle), wx*scale, wy*scale, wz*scale).normalized()

    def integrate(self, wx: float, wy: float, wz: float, dt: float,
                  *, body_frame: bool = True) -> "Quaternion":
        """Integrate one angular-velocity sample; choose frame convention explicitly."""
        delta = self.from_angular_velocity(wx, wy, wz, dt)
        return ((self * delta) if body_frame else (delta * self)).normalized()
