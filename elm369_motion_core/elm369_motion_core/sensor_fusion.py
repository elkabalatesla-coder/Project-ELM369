"""Basic complementary roll/pitch estimator; yaw needs a heading reference."""
from dataclasses import dataclass
from math import atan2,sqrt,isfinite
@dataclass(frozen=True)
class TiltEstimate:
    roll_radians: float
    pitch_radians: float
class ComplementaryTiltFilter:
    def __init__(self,*,gyro_weight=.98):
        if not isfinite(gyro_weight) or not 0<=gyro_weight<=1: raise ValueError("gyro_weight must be in [0,1]")
        self.gyro_weight=gyro_weight; self.roll=0.; self.pitch=0.; self.initialized=False
    def update(self,*,gyro_x,gyro_y,accel_x,accel_y,accel_z,dt):
        vals=(gyro_x,gyro_y,accel_x,accel_y,accel_z,dt)
        if not all(isfinite(v) for v in vals): raise ValueError("sensor values must be finite")
        if dt<0: raise ValueError("dt must be nonnegative")
        norm=sqrt(accel_x**2+accel_y**2+accel_z**2)
        if norm<1e-9:
            self.roll+=gyro_x*dt; self.pitch+=gyro_y*dt
            return TiltEstimate(self.roll,self.pitch)
        ar=atan2(accel_y,accel_z); ap=atan2(-accel_x,sqrt(accel_y**2+accel_z**2))
        if not self.initialized: self.roll,self.pitch,self.initialized=ar,ap,True
        else:
            a=self.gyro_weight
            self.roll=a*(self.roll+gyro_x*dt)+(1-a)*ar
            self.pitch=a*(self.pitch+gyro_y*dt)+(1-a)*ap
        return TiltEstimate(self.roll,self.pitch)
