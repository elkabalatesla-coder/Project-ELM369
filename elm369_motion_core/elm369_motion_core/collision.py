"""Axis-aligned bounding-box collision primitives."""
from dataclasses import dataclass
from math import isfinite
@dataclass(frozen=True)
class AABB:
    minimum: tuple[float,float,float]
    maximum: tuple[float,float,float]
    def __post_init__(self):
        if len(self.minimum)!=3 or len(self.maximum)!=3: raise ValueError("bounds must be 3-vectors")
        if not all(isfinite(v) for v in (*self.minimum,*self.maximum)): raise ValueError("bounds must be finite")
        if any(self.minimum[i]>self.maximum[i] for i in range(3)): raise ValueError("minimum must not exceed maximum")
    def intersects(self,other):
        return all(self.minimum[i]<=other.maximum[i] and self.maximum[i]>=other.minimum[i] for i in range(3))
    def translated(self,dx,dy,dz):
        if not all(isfinite(v) for v in (dx,dy,dz)): raise ValueError("translation must be finite")
        d=(dx,dy,dz)
        return AABB(tuple(self.minimum[i]+d[i] for i in range(3)),tuple(self.maximum[i]+d[i] for i in range(3)))
