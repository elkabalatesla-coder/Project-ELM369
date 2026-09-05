import unittest
from tools.elm_translator.glossary import translate
class T(unittest.TestCase):
    def test_hello(self):
        r = translate("hello", to="es")
        self.assertTrue(r["ok"])
        self.assertEqual(r["output"], "hola")
