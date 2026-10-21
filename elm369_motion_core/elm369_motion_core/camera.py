"""Engine-independent camera pose controls."""
from dataclasses import dataclass
from math import isfinite
from .quaternion import Quaternion
@dataclass(frozen=True)
class CameraPose:
    position: tuple[float,float,float]=(0.0,0.0,0.0)
    orientation: Quaternion=Quaternion()
class CameraController:
    """Backend-neutral look and translation controller; angles are radians."""
    def __init__(self,pose=None,*,sensitivity=1.0,max_pitch=1.553343034):
        if not isfinite(sensitivity) or sensitivity<=0: raise ValueError("sensitivity must be finite and positive")
        if not isfinite(max_pitch) or not 0<max_pitch<1.570796327: raise ValueError("max_pitch must be between zero and pi/2")
        self.pose=pose or CameraPose(); self.sensitivity=sensitivity; self.max_pitch=max_pitch
        self.pitch=0.0; self.yaw=0.0
    def look(self,dx,dy):
        if not isfinite(dx) or not isfinite(dy): raise ValueError("look input must be finite")
        self.yaw += dx*self.sensitivity
        self.pitch=max(-self.max_pitch,min(self.max_pitch,self.pitch-dy*self.sensitivity))
        y=Quaternion.from_angular_velocity(0,self.yaw,0,1)
        p=Quaternion.from_angular_velocity(self.pitch,0,0,1)
        self.pose=CameraPose(self.pose.position,(y*p).normalized()); return self.pose
    def move(self,dx,dy,dz):
        if not all(isfinite(v) for v in (dx,dy,dz)): raise ValueError("movement must be finite")
        p=self.pose.position
        self.pose=CameraPose((p[0]+dx,p[1]+dy,p[2]+dz),self.pose.orientation); return self.pose
