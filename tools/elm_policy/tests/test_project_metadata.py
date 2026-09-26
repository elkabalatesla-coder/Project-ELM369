import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class T(unittest.TestCase):
    def test_project_metadata_provenance_policy(self):
        data = json.loads((ROOT / "PROJECT_METADATA.json").read_text(encoding="utf-8"))
        policy = data["provenance_review_policy"]
        self.assertEqual(policy["access"], "pull_request_only_recommended")
        self.assertEqual(policy["policy"], "PROVENANCE_FIRST_REVIEW_REQUIRED")
        self.assertEqual(
            policy["disallowed_auto_actions"],
            [
                "push_to_github_when_authenticated",
                "ingest_local_state_without_explicit_consent",
            ],
        )
        self.assertTrue(policy["branch_protection"]["require_pull_request"])
        self.assertTrue(policy["branch_protection"]["require_codeowner_review"])
        self.assertTrue(policy["branch_protection"]["block_direct_push_to_main"])

    def test_project_metadata_uses_pending_detached_signature(self):
        data = json.loads((ROOT / "PROJECT_METADATA.json").read_text(encoding="utf-8"))
        signature = data["project_metadata"]["digital_signature"]
        self.assertEqual(signature["model"], "detached")
        self.assertIsNone(signature["signature"])
        self.assertEqual(signature["status"], "pending_external_generation")
