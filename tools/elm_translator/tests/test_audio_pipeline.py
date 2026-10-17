from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from tools.elm_translator.engine import translate_audio, translate_text
from tools.elm_translator.stt import SpeechToTextError, transcribe_audio
from tools.elm_translator.tts import TextToSpeechError, synthesize

class AudioPipelineTests(unittest.TestCase):
    def test_stt_uses_text_sidecar_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "input.wav"
            audio.write_bytes(b"placeholder audio")
            Path(tmp, "input.txt").write_text("hello", encoding="utf-8")
            result = transcribe_audio(audio)
            self.assertEqual(result["text"], "hello")
            self.assertTrue(result["fallback"])
            self.assertEqual(result["engine"], "text_sidecar_fallback")
    def test_stt_fails_without_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "input.wav"
            audio.write_bytes(b"placeholder audio")
            with self.assertRaises(SpeechToTextError): transcribe_audio(audio)
    def test_tts_fallback_is_text_not_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "speech.wav"
            result = synthesize("hola", target)
            self.assertFalse(result["audio_generated"])
            self.assertEqual(Path(result["output_path"]).read_text(encoding="utf-8"), "hola\n")
            self.assertFalse(target.exists())
    def test_tts_rejects_empty_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(TextToSpeechError): synthesize("  ", Path(tmp) / "speech.wav")
    def test_pipeline_uses_offline_glossary(self):
        result = translate_text("hello", to="es")
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], "hola")
        self.assertFalse(result["audio_generated"])
    def test_audio_pipeline_translates_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "input.wav"
            audio.write_bytes(b"placeholder audio")
            Path(tmp, "input.txt").write_text("hello", encoding="utf-8")
            result = translate_audio(audio, to="es", output_audio_path=Path(tmp) / "out.wav")
            self.assertTrue(result["ok"])
            self.assertEqual(result["translation"]["output"], "hola")
            self.assertFalse(result["audio_generated"])
            self.assertEqual(result["text_to_speech"]["engine"], "text_only_fallback")

if __name__ == "__main__": unittest.main()
