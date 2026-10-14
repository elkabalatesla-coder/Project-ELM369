"""Text-to-speech adapter with a truthful non-audio fallback.

A local synthesizer callable may be injected by an application that has a
supported offline TTS engine installed. Without one, this writes a UTF-8 text
artifact; it does not label that artifact as generated audio.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable, Any

class TextToSpeechError(RuntimeError):
    """Raised when input validation or synthesis fails."""

def synthesize(text: str, output_path: str | Path, *, synthesizer: Callable[[str, Path], Any] | None = None) -> dict[str, Any]:
    value = str(text).strip()
    if not value:
        raise TextToSpeechError("Text must not be empty.")
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if synthesizer is not None:
        try:
            synthesizer(value, target)
        except Exception as exc:
            raise TextToSpeechError(f"Local synthesizer failed: {exc}") from exc
        if not target.exists() or not target.is_file() or target.stat().st_size == 0:
            raise TextToSpeechError("Synthesizer returned without producing a non-empty file.")
        return {"ok": True, "audio_generated": True, "output_path": str(target), "engine": "injected_local_synthesizer", "fallback": False}
    fallback = target.with_suffix(".txt")
    fallback.write_text(value + "\n", encoding="utf-8")
    return {"ok": True, "audio_generated": False, "output_path": str(fallback), "requested_audio_path": str(target), "engine": "text_only_fallback", "fallback": True, "note": "Text saved; no audio was generated because no local TTS engine was supplied."}
