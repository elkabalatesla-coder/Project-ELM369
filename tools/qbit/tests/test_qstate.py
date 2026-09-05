import json
import unittest
from pathlib import Path

from tools.qbit import compute_qstate, recommend

ROOT = Path(__file__).resolve().parents[3]


class QbitTests(unittest.TestCase):
    def test_compute_qstate_weights(self):
        self.assertEqual(compute_qstate(1, 1, 1, 1), 1.0)
        self.assertEqual(compute_qstate(0, 0, 0, 0), 0.0)
        example = compute_qstate(0.85, 0.6, 0.9, 0.95)
        self.assertAlmostEqual(example, 0.8125, places=4)

    def test_recommend_hard_block_wins(self):
        self.assertEqual(recommend(0.99, hard_block=True), "ABORT")
        self.assertEqual(recommend(0.99, needs_authorization=True), "REQUEST_AUTHORIZATION")
        self.assertEqual(recommend(0.9), "ALLOW")

    def test_example_json_loads(self):
        path = ROOT / "schemas/qbit/examples/qbit.example.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        q = compute_qstate(**data["terms"])
        self.assertAlmostEqual(q, data["qstate"], places=4)


if __name__ == "__main__":
    unittest.main()
