import unittest
from elm369.intelligence import qbit, qstate, rolling_logic, critical_thinking, observable_workflow, random_protocol

class P1Tests(unittest.TestCase):
    def test_qbit_formula(self):
        self.assertEqual(qbit(1, 1, 1, 0), 0.85)
    def test_qstate_formula(self):
        self.assertEqual(qstate(1, 1, 1, 1), 1.0)
    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            qbit(1.1, .5, .5, .5)
    def test_rolling_logic_is_deterministic(self):
        self.assertEqual(rolling_logic("same"), rolling_logic("same"))
    def test_critical_engine_does_not_authorize(self):
        result = critical_thinking("test claim")
        self.assertEqual(result["authorization"], "NOT_GRANTED")
        self.assertEqual(result["assessment"], "INSUFFICIENT_EVIDENCE")
    def test_observable_workflow_requires_review(self):
        result = observable_workflow("sensor reading")
        self.assertEqual(result["gate"], "HUMAN_REVIEW_REQUIRED")
        self.assertIsNone(result["conclusion"])
    def test_random_disabled_by_default(self):
        with self.assertRaises(PermissionError):
            random_protocol(369, 3)
    def test_seeded_random_replays(self):
        self.assertEqual(random_protocol(369, 4, True), random_protocol(369, 4, True))

if __name__ == "__main__":
    unittest.main()
