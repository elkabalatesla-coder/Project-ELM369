"""Speech-to-text adapter with explicit offline fallback behavior.

No network calls are made. A caller may inject a recognizer callable. If none
is supplied, an adjacent .txt transcript sidecar can be used as a manual
fallback. This module never claims transcription when no result is available.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable, Any

class SpeechToTextError(RuntimeError):
    """Raised when transcription cannot be completed."""

def transcribe_audio(audio_path: str | Path, *, recognizer: Callable[[Path], str] | None = None, transcript_fallback: str | Path | None = None) -> dict[str, Any]:
    source = Path(audio_path)
    if not source.exists() or not source.is_file():
        raise SpeechToTextError(f"Audio source does not exist: {source}")
    if recognizer is not None:
        try:
            text = recognizer(source)
        except Exception as exc:
            if transcript_fallback is None:
                raise SpeechToTextError(f"Local recognizer failed: {exc}") from exc
            text = None
        if text is not None and str(text).strip():
            return {"ok": True, "text": str(text).strip(), "source": str(source), "engine": "injected_local_recognizer", "fallback": False}
    fallback = Path(transcript_fallback) if transcript_fallback else source.with_suffix(".txt")
    if fallback.exists() and fallback.is_file():
        text = fallback.read_text(encoding="utf-8").strip()
        if text:
            return {"ok": True, "text": text, "source": str(source), "engine": "text_sidecar_fallback", "fallback": True, "transcript_path": str(fallback)}
    raise SpeechToTextError("No offline recognizer result or transcript sidecar is available. Provide a local recognizer or a UTF-8 .txt sidecar.")
