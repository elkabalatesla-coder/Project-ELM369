"""Unit tests for the ELM369 gyroscope safety layer; run: python -m unittest discover -s tests."""
import unittest
from ELM369_Engine_Logic.gyro.processor import (
    GyroConfig, GyroSampleError, GyroscopeProcessor,
)


class GyroscopeProcessorTests(unittest.TestCase):
    def test_calibration_estimates_bias(self):
        p = GyroscopeProcessor()
        bias = p.calibrate([(0.01, -0.02, 0.03), (0.03, 0.00, 0.01)])
        self.assertAlmostEqual(bias[0], 0.02)
        self.assertTrue(p.calibrated)

    def test_bias_and_deadband_corrected(self):
        p = GyroscopeProcessor(GyroConfig(deadband_rad_s=0.005))
        p.calibrate([(0.01, 0.0, 0.0), (0.01, 0.0, 0.0)])
        reading = p.process(1.0, (0.012, 0.0, 0.0))
        self.assertEqual(reading.corrected_rad_s[1], 0.0)
        self.assertAlmostEqual(reading.corrected_rad_s[0], 0.0)

    def test_rejects_nonfinite_and_wrong_shape(self):
        p = GyroscopeProcessor()
        with self.assertRaises(GyroSampleError):
            p.process(1.0, (0.0, float("nan"), 0.0))
        with self.assertRaises(GyroSampleError):
            p.process(1.0, (0.0, 0.0))

    def test_rejects_nonmonotonic_timestamp(self):
        p = GyroscopeProcessor()
        p.process(1.0, (0.0, 0.0, 0.0))
        with self.assertRaises(GyroSampleError):
            p.process(1.0, (0.0, 0.0, 0.0))

    def test_gap_resets_filter_and_rejects_sample(self):
        p = GyroscopeProcessor()
        p.process(1.0, (0.0, 0.0, 0.0))
        with self.assertRaises(GyroSampleError):
            p.process(2.0, (0.0, 0.0, 0.0))
        self.assertIsNone(p._last_timestamp)

    def test_rejects_out_of_range_rate(self):
        p = GyroscopeProcessor()
        with self.assertRaises(GyroSampleError):
            p.process(1.0, (100.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
