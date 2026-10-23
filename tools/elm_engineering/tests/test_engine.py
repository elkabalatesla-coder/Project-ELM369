import contextlib
import io
import math
import unittest

from tools.elm_engineering import ELM369EngineeringCore
from tools.elm_engineering.__main__ import main


class EngineeringTests(unittest.TestCase):
    def setUp(self):
        self.core = ELM369EngineeringCore()

    def test_identifiers(self):
        self.assertEqual(self.core.project_id, "JMR0824197846902")
        self.assertEqual(
            ELM369EngineeringCore("JMR08241978202646902").project_id,
            "JMR08241978202646902",
        )

    def test_kinematics_forward_reconstruction(self):
        for x, y in [(15, 10), (-15, 10), (-15, -10), (15, -10)]:
            with self.subTest(x=x, y=y):
                result = self.core.compute_2d_inverse_kinematics(x, y, 12, 10)
                t1, t2 = map(math.radians, (
                    result["theta_1_deg"], result["theta_2_deg"]
                ))
                self.assertAlmostEqual(
                    12 * math.cos(t1) + 10 * math.cos(t1 + t2), x, delta=0.003
                )
                self.assertAlmostEqual(
                    12 * math.sin(t1) + 10 * math.sin(t1 + t2), y, delta=0.003
                )

    def test_workspace_and_boundaries(self):
        for x in [23, 1, 0]:
            self.assertIn("error", self.core.compute_2d_inverse_kinematics(x, 0, 12, 10))
        for x, expected in [(22, 0), (2, 180)]:
            result = self.core.compute_2d_inverse_kinematics(x, 0, 12, 10)
            self.assertEqual(result["theta_2_deg"], expected)
        result = self.core.compute_2d_inverse_kinematics(0, 0, 10, 10)
        self.assertEqual((result["theta_1_deg"], result["theta_2_deg"]), (0, 180))

    def test_kinematics_scale_and_roundoff(self):
        for scale in [1e-200, 1, 1e200]:
            result = self.core.compute_2d_inverse_kinematics(
                0.3 * scale, 0, 0.1 * scale, 0.2 * scale
            )
            self.assertEqual(result["theta_2_deg"], 0)
        with self.assertRaises(ValueError):
            self.core.compute_2d_inverse_kinematics(1e300, 0, 1e300, 1e-300)

    def test_invalid_kinematics(self):
        for index in range(4):
            for invalid in [math.nan, math.inf, -math.inf, True, "1", 10**1000]:
                values = [1, 1, 2, 2]
                values[index] = invalid
                with self.subTest(index=index, invalid=str(invalid)):
                    with self.assertRaises(ValueError):
                        self.core.compute_2d_inverse_kinematics(*values)
        for length in [0, -1]:
            for lengths in [(length, 1), (1, length)]:
                with self.assertRaises(ValueError):
                    self.core.compute_2d_inverse_kinematics(1, 1, *lengths)

    def test_pid_example(self):
        result = self.core.simulate_pid_control_step(
            210, 205.5, 1.2, 0.05, 0.1, 0.1, 2, 5
        )
        self.assertEqual(result, {
            "control_signal": 5.0225, "new_integral": 2.45, "current_error": 4.5
        })

    def test_pid_preserves_feedback_precision(self):
        integral, error = 0, 0
        for _ in range(10):
            result = self.core.simulate_pid_control_step(
                0.00001, 0, 0, 1, 0, 0.1, integral, error
            )
            integral, error = result["new_integral"], result["current_error"]
        self.assertAlmostEqual(integral, 0.00001)
        self.assertEqual(error, 0.00001)

    def test_invalid_pid_inputs_and_overflow(self):
        for index in range(8):
            for invalid in [math.nan, math.inf, -math.inf, True, "1"]:
                values = [1, 0, 1, 1, 1, 0.1, 0, 0]
                values[index] = invalid
                with self.assertRaises(ValueError):
                    self.core.simulate_pid_control_step(*values)
        for dt in [0, -0.1]:
            with self.assertRaises(ValueError):
                self.core.simulate_pid_control_step(1, 0, 1, 1, 1, dt, 0, 0)
        with self.assertRaises(ValueError):
            self.core.simulate_pid_control_step(1e308, -1e308, 1, 1, 1, 1, 0, 0)

    def test_resource_allocation(self):
        for gross in [0, 0.1, 10000]:
            result = self.core.evaluate_project_resource_allocation(gross)
            self.assertEqual(result["gross_value"], gross)
            self.assertEqual(result["charity_allocation"], gross * 0.01)
            self.assertAlmostEqual(
                result["charity_allocation"] + result["net_retained_resource"], gross
            )
            self.assertEqual(result["charity_targets"], [
                "Shriners", "Cancer/Stroke Research", "Human Trafficking Prevention"
            ])
        for invalid in [-1, math.nan, math.inf, -math.inf, True, "100"]:
            with self.assertRaises(ValueError):
                self.core.evaluate_project_resource_allocation(invalid)

    def test_demonstration(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        for text in ["KINEMATICS_SOLVED_SUCCESSFULLY", "5.0225", "100.0", "9900.0"]:
            self.assertIn(text, output.getvalue())


if __name__ == "__main__":
    unittest.main()
