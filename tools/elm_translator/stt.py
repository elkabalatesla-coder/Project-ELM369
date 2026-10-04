"""Speech-to-text adapters with deterministic offline fallback.

No audio is uploaded unless an explicitly configured provider is used.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Protocol


@dataclass(frozen=True)
class STTResult:
    text: str
    provider: str
    language: str
    offline: bool
    confidence: Optional[float] = None


class Recognizer(Protocol):
    def transcribe(self, audio_path: str, language: str = "en-US") -> STTResult: ...


class OfflineTextRecognizer:
    """Safe fallback for environments without an installed speech model.

    It accepts a UTF-8 transcript sidecar (<audio suffix>.txt), which makes
    pipeline tests and manual operation possible without pretending audio
    recognition occurred.
    """
    def transcribe(self, audio_path: str, language: str = "en-US") -> STTResult:
        path = Path(audio_path)
        sidecar = Path(str(path) + ".txt")
        if not sidecar.is_file():
            raise RuntimeError(
                "No offline STT model is configured. Install/configure Vosk "
                "or provide a UTF-8 transcript sidecar at "
                f"{sidecar}."
            )
        return STTResult(sidecar.read_text(encoding="utf-8").strip(),
                         "offline-sidecar", language, True, None)


class VoskRecognizer:
    """Optional local Vosk adapter; model files remain on the device."""
    def __init__(self, model_path: str):
        try:
            from vosk import Model, KaldiRecognizer
        except ImportError as exc:
            raise RuntimeError("Vosk is not installed; run: pip install vosk") from exc
        import wave
        self._wave = wave
        self._model = Model(model_path)
        self._recognizer_type = KaldiRecognizer

    def transcribe(self, audio_path: str, language: str = "en-US") -> STTResult:
        import json
        with self._wave.open(audio_path, "rb") as audio:
            if audio.getnchannels() != 1 or audio.getsampwidth() != 2:
                raise ValueError("Vosk expects mono, 16-bit PCM WAV audio.")
            recognizer = self._recognizer_type(self._model, audio.getframerate())
            chunks = []
            while True:
                data = audio.readframes(4000)
                if not data:
                    break
                if recognizer.AcceptWaveform(data):
                    chunks.append(json.loads(recognizer.Result()).get("text", ""))
            chunks.append(json.loads(recognizer.FinalResult()).get("text", ""))
        return STTResult(" ".join(x for x in chunks if x).strip(),
                         "vosk-local", language, True, None)


def build_recognizer(model_path: Optional[str] = None) -> Recognizer:
    if model_path:
        return VoskRecognizer(model_path)
    return OfflineTextRecognizer()
