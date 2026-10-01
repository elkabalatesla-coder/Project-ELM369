import json
import tempfile
import unittest
from pathlib import Path

from tools.elm_ai_tasks.cli import main
from tools.elm_ai_tasks.engine import evaluate, execute, list_tasks, monitor


TASK_ID = "text.keyword_extract"


class AiTaskTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.audit = Path(self.temp_dir.name) / "audit.jsonl"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registry_lists_bounded_offline_task(self):
        result = list_tasks()
        self.assertEqual(result["schema"], "elm369.ai_task_registry.v1")
        self.assertEqual(result["tasks"][0]["task_id"], TASK_ID)
        self.assertTrue(result["tasks"][0]["evaluation_required"])

    def test_run_requires_evaluation_then_returns_provenance(self):
        blocked = execute(TASK_ID, {"text": "alpha beta"}, audit_path=self.audit)
        self.assertEqual(blocked["error"], "evaluation_required")

        evaluation = evaluate(TASK_ID, audit_path=self.audit)
        self.assertTrue(evaluation["ok"])
        result = execute(TASK_ID, {"text": "alpha beta alpha"}, audit_path=self.audit)

        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], {"keywords": ["alpha", "beta"]})
        self.assertEqual(result["provenance"]["provider"], "builtin_rules")
        self.assertTrue(result["provenance"]["offline"])

    def test_mock_provider_is_offline_and_contract_compatible(self):
        evaluation = evaluate(TASK_ID, provider="mock", audit_path=self.audit)
        self.assertFalse(evaluation["ok"])
        result = execute(
            TASK_ID,
            {"text": "ignored"},
            provider="mock",
            audit_path=self.audit,
        )
        self.assertEqual(result["error"], "evaluation_required")

    def test_rejects_bad_inputs_restricted_data_and_sensitive_fields(self):
        self.assertEqual(
            execute(TASK_ID, {"text": 12}, audit_path=self.audit)["error"],
            "invalid_input_type",
        )
        self.assertEqual(
            execute(TASK_ID, {"text": "ok", "password": "hidden"}, audit_path=self.audit)["error"],
            "unexpected_input",
        )
        self.assertEqual(
            execute(
                TASK_ID,
                {"text": "ok"},
                data_classification="restricted",
                audit_path=self.audit,
            )["error"],
            "data_classification_not_allowed",
        )

    def test_audit_never_contains_input_or_output_content(self):
        evaluate(TASK_ID, audit_path=self.audit)
        secret_text = "unique-private-phrase-742"
        execute(TASK_ID, {"text": secret_text}, audit_path=self.audit)
        records = [json.loads(line) for line in self.audit.read_text().splitlines()]
        self.assertTrue(all("input" not in row and "output" not in row for row in records))
        self.assertNotIn(secret_text, self.audit.read_text())

    def test_monitor_summarizes_task_runs_and_evaluations(self):
        evaluate(TASK_ID, audit_path=self.audit)
        execute(TASK_ID, {"text": "alpha beta"}, audit_path=self.audit)
        report = monitor(self.audit)
        self.assertEqual(report["counts"]["evaluation:passed"], 1)
        self.assertEqual(report["counts"]["task_run:succeeded"], 3)

    def test_cli_evaluate_and_run(self):
        self.assertEqual(main(["evaluate", TASK_ID]), 0)
        self.assertEqual(main(["run", TASK_ID, "--input-json", '{"text":"alpha beta"}']), 0)

    def test_consequential_task_requires_human_approval_attestation(self):
        registry = json.loads(Path("data/registries/elm369_ai_tasks.json").read_text())
        registry["version"] = "test-approval"
        task = dict(registry["tasks"][0])
        task["task_id"] = "text.approval_test"
        task["consequential"] = True
        registry["tasks"] = [task]
        registry_path = Path(self.temp_dir.name) / "registry.json"
        registry_path.write_text(json.dumps(registry))
        self.assertTrue(evaluate(
            "text.approval_test",
            registry_path=registry_path,
            audit_path=self.audit,
        )["ok"])
        denied = execute(
            "text.approval_test",
            {"text": "alpha"},
            registry_path=registry_path,
            audit_path=self.audit,
        )
        self.assertEqual(denied["error"], "human_approval_required")
        allowed = execute(
            "text.approval_test",
            {"text": "alpha"},
            human_approved=True,
            approval_ref="operator-ticket-1",
            registry_path=registry_path,
            audit_path=self.audit,
        )
        self.assertTrue(allowed["ok"])
        self.assertTrue(allowed["provenance"]["human_approved"])


if __name__ == "__main__":
    unittest.main()
