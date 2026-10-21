import unittest
from elm369_motion_core.camera import CameraController
from elm369_motion_core.sensor_fusion import ComplementaryTiltFilter
from elm369_motion_core.collision import AABB
from elm369_motion_core.arcade_demo import GyroArcadeDemo
class CameraTests(unittest.TestCase):
    def test_move_look(self):
        c=CameraController(); self.assertEqual(c.move(1,2,3).position,(1,2,3)); self.assertAlmostEqual(c.look(.1,.1).orientation.norm(),1)
    def test_pitch_clamp(self):
        c=CameraController(max_pitch=1); c.look(0,-10); self.assertEqual(c.pitch,1)
    def test_nan_rejected(self):
        with self.assertRaises(ValueError): CameraController().look(float('nan'),0)
class SensorTests(unittest.TestCase):
    def test_gravity_initialization(self):
        o=ComplementaryTiltFilter().update(gyro_x=0,gyro_y=0,accel_x=0,accel_y=0,accel_z=1,dt=1/60); self.assertAlmostEqual(o.roll_radians,0)
    def test_negative_dt(self):
        with self.assertRaises(ValueError): ComplementaryTiltFilter().update(gyro_x=0,gyro_y=0,accel_x=0,accel_y=0,accel_z=1,dt=-1)
class CollisionTests(unittest.TestCase):
    def test_overlap(self):
        a=AABB((0,0,0),(1,1,1)); self.assertTrue(a.intersects(AABB((1,1,1),(2,2,2)))); self.assertFalse(a.intersects(AABB((2,2,2),(3,3,3))))
    def test_invalid(self):
        with self.assertRaises(ValueError): AABB((2,0,0),(1,1,1))
class ArcadeTests(unittest.TestCase):
    def test_score_once_per_contact_and_hazard(self):
        g=GyroArcadeDemo(lives=1); t=AABB((-.5,-.5,-.5),(.5,.5,.5)); h=AABB((-.5,-.5,-.5),(.5,.5,.5))
        self.assertEqual(g.step(tilt=0,dt=1/60,target=t,hazard=h).score,1)
        r=g.step(tilt=0,dt=1/60,target=t,hazard=h); self.assertEqual(r.score,1); self.assertTrue(r.game_over)
    def test_tilt_clamp(self):
        g=GyroArcadeDemo(); far=AABB((100,100,100),(101,101,101)); self.assertEqual(g.step(tilt=10,dt=1,target=far).player_x,5)
if __name__=='__main__': unittest.main()
