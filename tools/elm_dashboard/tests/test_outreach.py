import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.elm_dashboard.cli import main
from tools.elm_dashboard.outreach import build_outreach, render_outreach


class OutreachTests(unittest.TestCase):
    def test_categories_and_draft_status(self):
        portal = build_outreach()
        self.assertFalse(portal["communications_established"])
        self.assertFalse(portal["transmits"])
        records = portal["organizations"]
        self.assertEqual(len(records), 8)
        self.assertEqual(len({record["id"] for record in records}), 8)
        self.assertEqual({record["category"] for record in records}, {
            "university", "research_lab", "engineering_vendor", "charity"
        })
        for record in records:
            self.assertFalse(record["approved"])
            self.assertFalse(record["sent"])
            self.assertEqual(record["status"], "draft_pending_review")
            self.assertIn("before submission", record["draft"])
            self.assertNotEqual(record["source_status"], "verified")

    def test_no_network_or_automatic_submission(self):
        with patch("socket.socket", side_effect=AssertionError("Network forbidden")):
            html = render_outreach()
        self.assertIn("No messages sent", html)
        self.assertIn("form-action", html)
        for tag in ["<script", "<form", "<iframe", "<img", "<link"]:
            self.assertNotIn(tag, html.lower())
        self.assertIn('rel="noopener noreferrer"', html)

    def test_escape_directory_content(self):
        portal = build_outreach()
        portal["organizations"][0]["name"] = '<img src=x onerror="alert(1)"> &'
        portal["organizations"][0]["draft"] = "</pre><script>alert(1)</script>"
        with patch("tools.elm_dashboard.outreach.build_outreach", return_value=portal):
            html = render_outreach()
        self.assertIn("&lt;img", html)
        self.assertIn("&lt;/pre&gt;&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_reject_unsafe_links(self):
        for url in [
            "javascript:alert(1)", "http://example.org", "//example.org",
            "https://user@example.org", "https:///missing",
            "https://example.org/\nunsafe",
        ]:
            directory = {"organizations": [{"url": url}]}
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "directory.json"
                path.write_text(json.dumps(directory), encoding="utf-8")
                with patch("tools.elm_dashboard.outreach.DIRECTORY", path):
                    with self.assertRaises(ValueError):
                        build_outreach()

    def test_cli_formats(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["outreach"]), 0)
        self.assertEqual(json.loads(output.getvalue())["schema"], "elm369.outreach_portal.v1")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["outreach", "--format", "html"]), 0)
        self.assertTrue(output.getvalue().startswith("<!doctype html>"))

    def test_independent_of_working_directory(self):
        from tools.elm_dashboard.outreach import DIRECTORY
        self.assertTrue(DIRECTORY.is_absolute())
        self.assertTrue(DIRECTORY.is_file())


if __name__ == "__main__":
    unittest.main()
