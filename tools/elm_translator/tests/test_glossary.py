import unittest

from tools.elm_translator.cli import main
from tools.elm_translator.glossary import (
    coverage,
    languages,
    search,
    status,
    suggest,
    translate,
    translate_many,
)


class GlossaryTests(unittest.TestCase):
    def test_hello(self):
        r = translate("hello", to="es")
        self.assertTrue(r["ok"])
        self.assertEqual(r["output"], "hola")
        self.assertFalse(r["audio"])

    def test_operator_phrase(self):
        r = translate("access granted", to="fr")
        self.assertTrue(r["ok"])
        self.assertEqual(r["output"], "accès accordé")

    def test_missing_with_suggestions(self):
        r = translate("helo", to="es")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"], "not_in_glossary")
        self.assertIn("suggestions", r)
        self.assertTrue(any(s.lower() == "hello" for s in r["suggestions"]))

    def test_suggest_nearest(self):
        hits = suggest("thanky")
        self.assertTrue(any("thank" in h.lower() for h in hits))

    def test_missing(self):
        r = translate("xyzzy-not-a-phrase", to="es")
        self.assertFalse(r["ok"])
        self.assertEqual(r.get("suggestions"), [])

    def test_langs(self):
        langs = languages()
        self.assertIn("en", langs)
        self.assertIn("es", langs)
        self.assertIn("fr", langs)
        self.assertIn("de", langs)

    def test_batch(self):
        r = translate_many(["hello", "thank you"], to="de")
        self.assertTrue(r["ok"])
        self.assertEqual(r["count"], 2)

    def test_expanded_glossary_size(self):
        from tools.elm_translator.glossary import load

        entries = load().get("entries") or []
        self.assertGreaterEqual(len(entries), 40)

    def test_coverage(self):
        c = coverage()
        self.assertTrue(c["ok"])
        self.assertGreaterEqual(c["entry_count"], 40)
        self.assertTrue(c["complete"])
        self.assertFalse(c["audio"])

    def test_status_done(self):
        s = status()
        self.assertEqual(s["status"], "DONE")
        self.assertEqual(s["tool_id"], "AUDIO-TX")
        self.assertFalse(s["audio"])
        self.assertTrue(any("STT" in g for g in s["non_goals"]))

    def test_search(self):
        r = search("vault")
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["count"], 1)
        self.assertTrue(any(e.get("en", "").lower() == "vault" for e in r["matches"]))

    def test_cli_langs(self):
        self.assertEqual(main(["langs"]), 0)

    def test_cli_coverage(self):
        self.assertEqual(main(["coverage"]), 0)

    def test_cli_status(self):
        self.assertEqual(main(["status"]), 0)

    def test_cli_search(self):
        self.assertEqual(main(["search", "hello"]), 0)


if __name__ == "__main__":
    unittest.main()
