"""Offline speech/translation orchestration for ELM369 AUDIO-TX."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Callable
from . import glossary
from .stt import transcribe_audio
from .tts import synthesize

def translate_text(text: str, *, to: str = "es") -> dict[str, Any]:
    result = glossary.translate(text, to=to)
    result["pipeline"] = "offline_glossary"
    result["audio_generated"] = False
    return result

def translate_audio(audio_path: str | Path, *, to: str = "es", transcript_fallback: str | Path | None = None, recognizer: Callable[[Path], str] | None = None, output_audio_path: str | Path | None = None, synthesizer: Callable[[str, Path], Any] | None = None) -> dict[str, Any]:
    speech = transcribe_audio(audio_path, recognizer=recognizer, transcript_fallback=transcript_fallback)
    translated = glossary.translate(speech["text"], to=to)
    result: dict[str, Any] = {"ok": bool(translated.get("ok")), "pipeline": "offline_stt_glossary_tts", "speech_to_text": speech, "translation": translated, "text_to_speech": None, "project_id": translated.get("project_id", glossary.PROJECT_ID), "watermark": glossary.WATERMARK}
    if translated.get("ok") and output_audio_path is not None:
        result["text_to_speech"] = synthesize(str(translated["output"]), output_audio_path, synthesizer=synthesizer)
    result["audio_generated"] = bool(result["text_to_speech"] and result["text_to_speech"].get("audio_generated"))
    return result
