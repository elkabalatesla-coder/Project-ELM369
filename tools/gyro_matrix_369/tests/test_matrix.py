import math
import unittest

from tools.gyro_matrix_369 import build_matrix, transform
from tools.gyro_matrix_369.cli import main


class GyroMatrixTests(unittest.TestCase):
    def test_zero_rates_produce_identity(self):
        matrix = build_matrix((0, 0, 0), 0.01)
        for row in range(9):
            for column in range(9):
                self.assertEqual(matrix[row][column], 1.0 if row == column else 0.0)

    def test_transform_preserves_vector_norm(self):
        vector = (1, -2, 3, 4, -5, 6, 7, -8, 9)
        matrix = build_matrix((1.2, -0.7, 2.5), 0.04)
        output = transform(matrix, vector)
        self.assertAlmostEqual(sum(value * value for value in output), sum(value * value for value in vector))

    def test_matrix_rows_are_orthonormal(self):
        matrix = build_matrix((0.5, -1.1, 2.0), 0.02)
        for left in range(9):
            for right in range(9):
                dot_product = sum(matrix[left][i] * matrix[right][i] for i in range(9))
                self.assertAlmostEqual(dot_product, 1.0 if left == right else 0.0)

    def test_large_finite_rates_remain_bounded(self):
        matrix = build_matrix((1e300, -1e300, 1e300), 1e300)
        self.assertTrue(all(math.isfinite(value) for row in matrix for value in row))

    def test_rejects_invalid_inputs(self):
        for rates, dt in (((0, 1), 0.1), ((0, math.inf, 0), 0.1), ((0, 0, 0), 0)):
            with self.subTest(rates=rates, dt=dt), self.assertRaises(ValueError):
                build_matrix(rates, dt)

    def test_rejects_malformed_transform_inputs(self):
        with self.assertRaises(ValueError):
            transform(build_matrix((0, 0, 0), 0.1), (0,) * 8)
        with self.assertRaises(ValueError):
            transform(((1.0,),), (0,) * 9)

    def test_cli_emits_matrix_without_actuation(self):
        self.assertEqual(main(["0", "0", "0", "--dt", "0.01"]), 0)


if __name__ == "__main__":
    unittest.main()
