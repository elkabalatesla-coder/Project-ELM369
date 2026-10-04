import unittest
from tools.elm_translator.engine import Glossary, TranslatorEngine


class FakeRecognizer:
    def transcribe(self, audio_path, language="en-US"):
        from tools.elm_translator.stt import STTResult
        return STTResult("hello project", "fake", language, True)


class FakeTTS:
    def synthesize(self, text, language="en", output_path=None):
        from tools.elm_translator.tts import TTSResult
        return TTSResult(True, "fake", True, output_path)


class TranslatorTests(unittest.TestCase):
    def setUp(self):
        self.engine = TranslatorEngine(Glossary.load(),
                                       recognizer=FakeRecognizer(),
                                       synthesizer=FakeTTS())

    def test_glossary_translation(self):
        result = self.engine.translate_text("Hello, project!", "en", "es")
        self.assertEqual(result.translated_text, "Hola, proyecto!")
        self.assertEqual(result.glossary_hits, 2)

    def test_glossary_case_preservation(self):
        result = self.engine.translate_text("HELLO", "en", "es")
        self.assertEqual(result.translated_text, "HOLA")

    def test_same_language_is_unchanged(self):
        result = self.engine.translate_text("hello", "en", "en")
        self.assertEqual(result.translated_text, "hello")

    def test_audio_pipeline(self):
        result = self.engine.process_audio("sample.wav", speak=True)
        self.assertEqual(result["translation"].translated_text, "hola proyecto")
        self.assertTrue(result["tts"].spoken)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.translate_text("  ", "en", "es")


if __name__ == "__main__":
    unittest.main()
