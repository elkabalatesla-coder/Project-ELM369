import unittest

from tools.elm_translator.cli import main
from tools.elm_translator.glossary import languages, translate, translate_many


class GlossaryTests(unittest.TestCase):
    def test_hello(self):
        r = translate("hello", to="es")
        self.assertTrue(r["ok"])
        self.assertEqual(r["output"], "hola")
        self.assertFalse(r["audio"])

    def test_missing(self):
        r = translate("xyzzy-not-a-phrase", to="es")
        self.assertFalse(r["ok"])

    def test_langs(self):
        langs = languages()
        self.assertIn("en", langs)
        self.assertIn("es", langs)

    def test_batch(self):
        r = translate_many(["hello", "thank you"], to="de")
        self.assertTrue(r["ok"])
        self.assertEqual(r["count"], 2)

    def test_cli_langs(self):
        self.assertEqual(main(["langs"]), 0)


if __name__ == "__main__":
    unittest.main()
