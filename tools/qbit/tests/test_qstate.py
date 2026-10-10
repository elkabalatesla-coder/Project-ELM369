import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.qbit import calibrate_weights, compute_qstate, recommend
from tools.qbit.__main__ import main

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

    def test_calibration_proposes_normalized_weights_without_applying(self):
        samples = [
            {"terms": {"L": 1, "M": 0, "R": 0, "H": 0}, "target_qstate": 1},
            {"terms": {"L": 0, "M": 1, "R": 0, "H": 0}, "target_qstate": 0},
            {"terms": {"L": 0, "M": 0, "R": 1, "H": 0}, "target_qstate": 0},
            {"terms": {"L": 0, "M": 0, "R": 0, "H": 1}, "target_qstate": 0},
        ]
        result = calibrate_weights(samples)

        self.assertGreater(result["weights"]["L"], 0.85)
        self.assertAlmostEqual(sum(result["weights"].values()), 1.0)
        self.assertLess(result["calibrated_mae"], result["baseline_mae"])
        self.assertFalse(result["applied"])
        self.assertEqual(compute_qstate(1, 0, 0, 0), 0.4)

    def test_calibration_rejects_insufficient_and_invalid_samples(self):
        with self.assertRaisesRegex(ValueError, "at least four"):
            calibrate_weights([])
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            calibrate_weights([
                {"terms": {"L": 1.1, "M": 0, "R": 0, "H": 0}, "target_qstate": 0}
                for _ in range(4)
            ])
        with self.assertRaisesRegex(ValueError, "finite number"):
            calibrate_weights([
                {"terms": {"L": float("nan"), "M": 0, "R": 0, "H": 0}, "target_qstate": 0}
                for _ in range(4)
            ])

    def test_calibration_cli_writes_payload_free_audit_record(self):
        samples = [
            {"terms": {"L": 1, "M": 0, "R": 0, "H": 0}, "target_qstate": 1},
            {"terms": {"L": 0, "M": 1, "R": 0, "H": 0}, "target_qstate": 0},
            {"terms": {"L": 0, "M": 0, "R": 1, "H": 0}, "target_qstate": 0},
            {"terms": {"L": 0, "M": 0, "R": 0, "H": 1}, "target_qstate": 0},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "samples.json"
            log_path = Path(temp_dir) / "calibration.jsonl"
            sample_path.write_text(json.dumps(samples), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["calibrate", str(sample_path), "--log", str(log_path)]), 0)

            record = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(record["event"], "qbit_weight_calibration")
            self.assertFalse(record["applied"])
            self.assertNotIn("terms", record)


if __name__ == "__main__":
    unittest.main()
