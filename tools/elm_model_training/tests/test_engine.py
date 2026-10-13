import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.elm_model_training.cli import main
from tools.elm_model_training.engine import REGISTRY, catalog, list_plans, plan


class ModelTrainingTests(unittest.TestCase):
    def test_catalog(self):
        result = catalog()
        self.assertFalse(result["training_enabled"])
        self.assertTrue(any(p["id"] == "rag_copilot" for p in result["profiles"]))

    def test_plan_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "plans.jsonl"
            with mock.patch("tools.elm_model_training.engine.STORE", store):
                created = plan("support copilot refresh", dataset="support_faq_v3")
                self.assertTrue(created["ok"])
                self.assertEqual(created["profile"], "rag_copilot")
                self.assertFalse(created["training_enabled"])
                rows = list_plans()
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["plan_id"], created["plan_id"])

    def test_unknown_profile(self):
        created = plan("support copilot refresh", profile="missing")
        self.assertFalse(created["ok"])
        self.assertEqual(created["error"], "unknown_profile")

    def test_cli_catalog(self):
        self.assertEqual(main(["catalog"]), 0)


if __name__ == "__main__":
    unittest.main()
