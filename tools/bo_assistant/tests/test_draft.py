import json
import unittest

from tools.bo_assistant.cli import main
from tools.bo_assistant.draft import draft, multi_turn_template


class DraftTests(unittest.TestCase):
    def test_draft_never_sends(self):
        r = draft("status please", channel="email", tone="government")
        self.assertFalse(r["sends"])
        self.assertIn("Subject", r["draft"])
        self.assertIn("Kokomo", r["draft"])
        self.assertIn("never transmits", r["draft"])
        self.assertEqual(r["provenance"]["vault_primary"], "JMR08241978202646902")
        self.assertEqual(r["provenance"]["vault_companion"], "JMR0824197846902")

    def test_sms_footer(self):
        r = draft("ping", channel="sms", tone="corporate")
        self.assertIn("IX JR", r["draft"])
        self.assertIn("46902", r["draft"])
        self.assertFalse(r["sends"])

    def test_phone_script_no_dial(self):
        r = draft("call script", channel="phone", tone="formal")
        self.assertIn("do not auto-dial", r["draft"])
        self.assertFalse(r["sends"])

    def test_multi_turn(self):
        prior = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi — how can I help?"},
        ]
        r = multi_turn_template("need a reschedule", prior_turns=prior)
        self.assertEqual(r["turn_count"], 3)
        self.assertEqual(r["template"], "multi_turn_v1")
        self.assertIn("Prior thread", r["draft"])
        self.assertFalse(r["sends"])

    def test_invalid_channel(self):
        with self.assertRaises(ValueError):
            draft("x", channel="carrier-pigeon")

    def test_cli_draft(self):
        self.assertEqual(main(["draft", "hello", "--channel", "sms"]), 0)

    def test_cli_multi_turn(self):
        turns = json.dumps([{"role": "user", "content": "a"}])
        self.assertEqual(
            main(["multi-turn", "b", "--prior-turns", turns]),
            0,
        )


if __name__ == "__main__":
    unittest.main()
