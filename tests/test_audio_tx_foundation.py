"""Regression tests for the existing ELM369 AUDIO-TX foundation branch."""
import tempfile
import unittest
from pathlib import Path

from tools.elm_translator.engine import Glossary, TranslatorEngine
from tools.elm_translator.stt import OfflineTextRecognizer, STTResult
from tools.elm_translator.tts import SystemTTS, TTSResult


class FakeRecognizer:
    def __init__(self, text="hello"):
        self.text = text

    def transcribe(self, audio_path, language="en-US"):
        return STTResult(self.text, "fake", language, True, 0.99)


class FakeSynthesizer:
    def synthesize(self, text, language="en", output_path=None):
        return TTSResult(bool(text.strip()), "fake", True, output_path)


class AudioTXFoundationTests(unittest.TestCase):
    def test_glossary_translation_preserves_punctuation_and_case(self):
        glossary = Glossary([{"en": "hello", "es": "hola"}], ["en", "es"])
        translated, hits = glossary.translate("HELLO!", "en", "es")
        self.assertEqual(translated, "HOLA!")
        self.assertEqual(hits, 1)

    def test_longest_phrase_is_not_retranslated_by_shorter_term(self):
        glossary = Glossary([
            {"en": "project elm369", "es": "Project ELM369"},
            {"en": "project", "es": "proyecto"},
        ], ["en", "es"])
        translated, hits = glossary.translate("Project ELM369", "en", "es")
        self.assertEqual(translated, "Project ELM369")
        self.assertEqual(hits, 1)

    def test_same_language_is_passthrough(self):
        glossary = Glossary([{"en": "hello", "es": "hola"}], ["en", "es"])
        self.assertEqual(glossary.translate("hello", "en", "en"), ("hello", 0))

    def test_unsupported_language_pair_is_rejected(self):
        glossary = Glossary([], ["en", "es"])
        with self.assertRaises(ValueError):
            glossary.translate("hello", "en", "fr")

    def test_empty_source_text_is_rejected(self):
        engine = TranslatorEngine(glossary=Glossary([], ["en"]))
        with self.assertRaises(ValueError):
            engine.translate_text("   ", "en", "en")

    def test_offline_sidecar_recognizer_reads_utf8_transcript(self):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = Path(directory) / "sample.wav"
            sidecar = Path(str(audio_path) + ".txt")
            sidecar.write_text("offline transcript", encoding="utf-8")
            result = OfflineTextRecognizer().transcribe(str(audio_path), "en-US")
        self.assertEqual(result.text, "offline transcript")
        self.assertEqual(result.provider, "offline-sidecar")
        self.assertTrue(result.offline)

    def test_missing_offline_sidecar_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = Path(directory) / "missing.wav"
            with self.assertRaisesRegex(RuntimeError, "No offline STT model"):
                OfflineTextRecognizer().transcribe(str(audio_path))

    def test_audio_pipeline_uses_injected_local_adapters(self):
        glossary = Glossary([{"en": "hello", "es": "hola"}], ["en", "es"])
        engine = TranslatorEngine(glossary=glossary, recognizer=FakeRecognizer(),
                                  synthesizer=FakeSynthesizer())
        result = engine.process_audio("unused.wav", "en", "es", speak=True)
        self.assertEqual(result["translation"].translated_text, "hola")
        self.assertTrue(result["tts"].spoken)

    def test_tts_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            SystemTTS(command="not-installed-test-command").synthesize("  ", "en")


if __name__ == "__main__":
    unittest.main()
