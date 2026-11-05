import math
import unittest

from elm369_motion_core.matrix import identity4, multiply4, transform_point
from elm369_motion_core.quaternion import Quaternion
from elm369_motion_core.scoring import DecisionInputs, score_action
from elm369_motion_core.runtime import DeterministicMotionRuntime


class MatrixTests(unittest.TestCase):
    def test_identity_transform(self):
        self.assertEqual(transform_point(identity4(), (1, 2, 3, 1)),
                         (1.0, 2.0, 3.0, 1.0))

    def test_identity_product(self):
        self.assertEqual(multiply4(identity4(), identity4()), identity4())

    def test_reject_bad_matrix(self):
        with self.assertRaises(ValueError):
            transform_point(((1, 2),), (1, 2, 3, 1))


class QuaternionTests(unittest.TestCase):
    def test_zero_angular_velocity_keeps_identity(self):
        self.assertEqual(Quaternion.from_angular_velocity(0, 0, 0, 1), Quaternion())

    def test_z_axis_rotation(self):
        q = Quaternion.from_angular_velocity(0, 0, math.pi, 1)
        self.assertAlmostEqual(q.w, 0.0, places=7)
        self.assertAlmostEqual(q.z, 1.0, places=7)

    def test_negative_dt_rejected(self):
        with self.assertRaises(ValueError):
            Quaternion.from_angular_velocity(0, 0, 1, -0.1)


class ScoringTests(unittest.TestCase):
    def test_risk_gate_overrides_high_score(self):
        result = score_action(DecisionInputs(1, 1, 1, 0.9), max_risk=0.7)
        self.assertTrue(result.accepted_by_score)
        self.assertFalse(result.risk_gate_passed)
        self.assertEqual(result.reason, "blocked_by_risk_gate")

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            score_action(DecisionInputs(1.1, 0, 0, 0))


class RuntimeTests(unittest.TestCase):
    def test_fixed_step_and_replay_hash(self):
        a = DeterministicMotionRuntime()
        b = DeterministicMotionRuntime()
        for _ in range(10):
            a.step((0, 0, 1), (1, 0, 0))
            b.step((0, 0, 1), (1, 0, 0))
        self.assertEqual(a.state.tick, 10)
        self.assertAlmostEqual(a.state.position[0], 10 / 60)
        self.assertEqual(a.replay_hash(), b.replay_hash())

    def test_nonfinite_input_rejected(self):
        with self.assertRaises(ValueError):
            DeterministicMotionRuntime().step((float("nan"), 0, 0))


if __name__ == "__main__":
    unittest.main()
