import unittest

from tools.elm_obfuscate.cipher import deobfuscate, obfuscate


class CipherTests(unittest.TestCase):
    def test_roundtrip(self):
        msg = "Hello ELM369 vault notes!"
        c = obfuscate(msg)
        self.assertNotEqual(c, msg)
        self.assertEqual(deobfuscate(c), msg)


if __name__ == "__main__":
    unittest.main()
