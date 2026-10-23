import contextlib
import io
import unittest
from html.parser import HTMLParser
from unittest.mock import patch

from tools.elm_engineering.dashboard import TEMPLATE, main, render_dashboard
from tools.elm_engineering.master import ELM369MasterSimulation


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if "href" in attrs:
            self.links.append(attrs["href"])


class DashboardTests(unittest.TestCase):
    def test_calculated_results_and_safety_labels(self):
        page = render_dashboard()
        for text in [
            "JMR0824197846902", "JMR08241978202646902", "2.0003", "2292.0",
            "22.92", "9.65", "12.82", "12.5", "82.0", "680.4",
            "50000.0", "500.0", "49500.0", "PENDING_HUMAN_REVIEW",
            "Offline simulation only", "No donations, payments", "not additive",
            "Scalar dimension check only",
        ]:
            self.assertIn(text, page)
        self.assertNotIn("<!-- ELM369_REPORT -->", page)
        self.assertNotIn("Generate your calculated report", page)
        self.assertTrue(page.startswith("<!doctype html>"))

    def test_semantic_sections_and_local_only_links(self):
        parser = PageParser()
        parser.feed(render_dashboard())
        self.assertEqual(parser.tags.count("h1"), 1)
        self.assertEqual(parser.tags.count("article"), 3)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        for link in parser.links:
            self.assertTrue(link.startswith("#"))
            self.assertIn(link[1:], parser.ids)
        for tag in ["script", "iframe", "img", "form", "link"]:
            self.assertNotIn(tag, parser.tags)
        self.assertIn("details", parser.tags)
        self.assertIn("summary", parser.tags)

    def test_report_content_is_escaped(self):
        report = ELM369MasterSimulation().run_full_simulation()
        attack = '</pre><script>alert("x")</script><img src=x onerror=alert(1)> &'
        report["simulation_header"]["system_id_primary"] = attack
        report["domain_results"][0]["domain"] = attack
        report["domain_results"][0]["gcode_preview"] = [attack]
        report["governance_audit"]["basis"] = attack
        with patch(
            "tools.elm_engineering.dashboard.ELM369MasterSimulation.run_full_simulation",
            return_value=report,
        ):
            page = render_dashboard()
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&amp;", page)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img", page)

    def test_single_snapshot_and_output_follows_calculations(self):
        report = ELM369MasterSimulation().run_full_simulation()
        report["domain_results"][2]["energy_savings_usd"] = 123.45
        with patch(
            "tools.elm_engineering.dashboard.ELM369MasterSimulation.run_full_simulation",
            return_value=report,
        ) as simulate:
            page = render_dashboard()
        simulate.assert_called_once_with()
        self.assertIn("<dd>123.45</dd>", page)

    def test_offline_cli_and_absolute_template(self):
        self.assertTrue(TEMPLATE.is_absolute())
        self.assertTrue(TEMPLATE.is_file())
        output = io.StringIO()
        with patch("socket.socket", side_effect=AssertionError("No network")), contextlib.redirect_stdout(output):
            main()
        self.assertIn("<title>ELM369 Engineering Simulation Dashboard</title>", output.getvalue())
        self.assertIn("default-src 'none'", output.getvalue())

    def test_model_errors_do_not_generate_success_page(self):
        with patch(
            "tools.elm_engineering.dashboard.ELM369MasterSimulation.run_full_simulation",
            side_effect=ValueError("Invalid model"),
        ):
            with self.assertRaises(ValueError):
                render_dashboard()


if __name__ == "__main__":
    unittest.main()
