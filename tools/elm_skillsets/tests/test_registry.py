import unittest

from tools.elm_skillsets.cli import main
from tools.elm_skillsets.registry import get_skillset, get_skillsets, render_guidance


class SkillsetTests(unittest.TestCase):
    def test_lists_ai_and_writing_categories(self):
        self.assertTrue(get_skillsets("ai"))
        self.assertTrue(get_skillsets("Writing"))
        self.assertEqual(get_skillsets("unknown"), [])

    def test_get_skillset_is_case_insensitive(self):
        self.assertEqual(get_skillset("writing-grammar")["category"], "Writing")
        with self.assertRaises(KeyError):
            get_skillset("missing")

    def test_render_guidance(self):
        guidance = render_guidance(["AI-RESEARCH", "WRITING-SPELLING"])
        self.assertIn("AI-assisted research", guidance)
        self.assertIn("Spelling and word choice", guidance)
        self.assertIn("Do not invent sources", guidance)

    def test_cli_rejects_unknown_skill(self):
        with self.assertRaises(SystemExit) as error:
            main(["guidance", "missing"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
