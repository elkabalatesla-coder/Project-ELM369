"""ELM369 translation pipeline: STT -> glossary-preserving translation -> TTS."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Dict, Iterable, Optional

from .stt import STTResult, build_recognizer
from .tts import TTSResult, build_synthesizer


@dataclass(frozen=True)
class TranslationResult:
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    glossary_hits: int
    offline: bool


class Glossary:
    def __init__(self, entries: Iterable[dict], languages: Iterable[str]):
        self.languages = tuple(languages)
        self.entries = tuple(entries)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Glossary":
        source = Path(path) if path else Path(__file__).parent / "data" / "glossary.json"
        if not source.exists():
            return cls((), ("en",))
        payload = json.loads(source.read_text(encoding="utf-8"))
        return cls(payload.get("entries", []), payload.get("languages", ["en"]))

    def translate(self, text: str, source: str, target: str) -> tuple[str, int]:
        if source == target:
            return text, 0
        if source not in self.languages or target not in self.languages:
            raise ValueError(f"Unsupported glossary language pair: {source}->{target}")
        result, hits = text, 0
        # Longest phrases first; preserve original casing and punctuation.
        pairs = []
        for entry in self.entries:
            if source in entry and target in entry:
                pairs.append((entry[source], entry[target]))
        for term, replacement in sorted(pairs, key=lambda p: len(p[0]), reverse=True):
            pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
            result, count = pattern.subn(lambda m: _match_case(m.group(0), replacement), result)
            hits += count
        return result, hits


def _match_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original.istitle():
        return replacement.title()
    return replacement


class TranslatorEngine:
    def __init__(self, glossary: Optional[Glossary] = None, recognizer=None, synthesizer=None):
        self.glossary = glossary or Glossary.load()
        self.recognizer = recognizer or build_recognizer()
        self.synthesizer = synthesizer or build_synthesizer()

    def translate_text(self, text: str, source_language: str = "en",
                       target_language: str = "es") -> TranslationResult:
        if not text.strip():
            raise ValueError("Source text must not be empty.")
        translated, hits = self.glossary.translate(text, source_language, target_language)
        return TranslationResult(text, translated, source_language, target_language, hits, True)

    def transcribe_audio(self, audio_path: str, language: str = "en-US") -> STTResult:
        return self.recognizer.transcribe(audio_path, language)

    def speak(self, text: str, language: str = "en",
              output_path: Optional[str] = None) -> TTSResult:
        return self.synthesizer.synthesize(text, language, output_path)

    def process_audio(self, audio_path: str, source_language: str = "en",
                      target_language: str = "es", speak: bool = False) -> dict:
        stt = self.transcribe_audio(audio_path, source_language)
        translation = self.translate_text(stt.text, source_language, target_language)
        tts = self.speak(translation.translated_text, target_language) if speak else None
        return {"stt": stt, "translation": translation, "tts": tts}


def _main():
    import argparse
    parser = argparse.ArgumentParser(description="ELM369 offline-first translator")
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument("--source", default="en")
    parser.add_argument("--target", default="es")
    parser.add_argument("--glossary")
    args = parser.parse_args()
    engine = TranslatorEngine(Glossary.load(args.glossary))
    if not args.text:
        parser.error("Provide text. Audio transcription is available through the Python API.")
    result = engine.translate_text(args.text, args.source, args.target)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
