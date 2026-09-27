import unittest

from tools.elm_security.cli import main
from tools.elm_security.security import (
    CANONICAL_ID,
    COMPANION_ID,
    build_security_posture,
    list_security_tools,
    registry_summary,
    resolve_identity,
)


class ElmSecurityTests(unittest.TestCase):
    def test_resolve_identity_success(self):
        result = resolve_identity([CANONICAL_ID, COMPANION_ID], observed_at="2026-09-27T00:00:00+00:00")
        self.assertTrue(result["integrity_status"]["ok"])
        self.assertTrue(result["integrity_status"]["provenance_distinct"])
        self.assertEqual(result["resolved_identity"]["canonical"], CANONICAL_ID)

    def test_resolve_identity_missing_companion(self):
        result = resolve_identity([CANONICAL_ID], observed_at="2026-09-27T00:00:00+00:00")
        self.assertFalse(result["integrity_status"]["ok"])
        self.assertFalse(result["integrity_status"]["companion_identifier_exists"])

    def test_registry_filters(self):
        tools = list_security_tools(required_for="vulnerability_prioritization")
        self.assertTrue(any(tool["name"] == "CISA KEV" for tool in tools))
        self.assertTrue(all("vulnerability_prioritization" in tool.get("required_for", []) for tool in tools))

    def test_registry_summary(self):
        summary = registry_summary()
        self.assertGreaterEqual(summary["tool_count"], 3)
        self.assertIn("threat_intelligence", summary["categories"])

    def test_build_security_posture(self):
        posture = build_security_posture()
        self.assertTrue(posture["ok"])
        self.assertIn("identity", posture)
        self.assertIn("registry", posture)

    def test_cli_verify(self):
        self.assertEqual(main(["verify"]), 0)


if __name__ == "__main__":
    unittest.main()
