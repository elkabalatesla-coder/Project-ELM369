import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.elm_translator.cli import main
from tools.elm_translator.glossary import languages, translate, translate_file, translate_many


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

    def test_translate_file_text(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "phrases.txt"
            path.write_text("hello\nthank you\n\n", encoding="utf-8")
            result = translate_file(path, to="fr")
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["input_format"], "text")
        self.assertEqual(result["results"][0]["output"], "bonjour")

    def test_translate_file_json(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "phrases.json"
            path.write_text('["hello", "vault"]\n', encoding="utf-8")
            result = translate_file(path, to="es")
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["input_format"], "json")
        self.assertEqual(result["results"][1]["output"], "bóveda")

    def test_translate_file_missing(self):
        result = translate_file("/tmp/does-not-exist-elm369.txt", to="es")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "input_file_not_found")

    def test_cli_file_output(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "phrases.txt"
            target = Path(tmp) / "out.json"
            source.write_text("hello\nplease\n", encoding="utf-8")
            rc = main(["file", str(source), "--to", "de", "--out", str(target)])
            self.assertEqual(rc, 0)
            self.assertIn('"hallo"', target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
