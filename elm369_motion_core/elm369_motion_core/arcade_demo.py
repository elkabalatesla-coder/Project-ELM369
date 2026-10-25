"""Small renderer-independent deterministic arcade gameplay model."""
from dataclasses import dataclass
from math import isfinite
from .collision import AABB
@dataclass(frozen=True)
class ArcadeSnapshot:
    tick:int
    player_x:float
    score:int
    lives:int
    game_over:bool
class GyroArcadeDemo:
    def __init__(self,*,player_x=0.,speed=5.,half_width=.5,lives=3):
        if not all(isfinite(v) for v in (player_x,speed,half_width)) or speed<=0 or half_width<=0 or lives<1: raise ValueError("invalid player, speed, width, or lives")
        self.tick=0; self.player_x=player_x; self.speed=speed; self.half_width=half_width
        self.score=0; self.lives=lives; self.game_over=False; self._overlapping_target=False; self._overlapping_hazard=False
    def step(self,*,tilt,dt,target,hazard=None):
        if not isfinite(tilt) or not isfinite(dt) or dt<0: raise ValueError("tilt must be finite and dt finite/nonnegative")
        if self.game_over: return self.snapshot()
        self.player_x+=max(-1.,min(1.,tilt))*self.speed*dt; self.tick+=1
        player=AABB((self.player_x-self.half_width,-.5,-.5),(self.player_x+self.half_width,.5,.5))
        touching=player.intersects(target)
        if touching and not self._overlapping_target: self.score+=1
        self._overlapping_target=touching
        danger=hazard is not None and player.intersects(hazard)
        if danger and not self._overlapping_hazard:
            self.lives=max(0,self.lives-1)
            if self.lives==0: self.game_over=True
        self._overlapping_hazard=danger
        return self.snapshot()
    def snapshot(self):
        return ArcadeSnapshot(self.tick,self.player_x,self.score,self.lives,self.game_over)
