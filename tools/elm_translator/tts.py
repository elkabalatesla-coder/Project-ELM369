"""Text-to-speech adapters with explicit local/offline behavior."""
from __future__ import annotations
from dataclasses import dataclass
import shutil
import subprocess
from typing import Optional


@dataclass(frozen=True)
class TTSResult:
    spoken: bool
    provider: str
    offline: bool
    output_path: Optional[str] = None


class SpeechSynthesizer:
    def synthesize(self, text: str, language: str = "en", output_path: Optional[str] = None) -> TTSResult:
        raise NotImplementedError


class SystemTTS:
    """Uses an installed local command; never silently falls back to a cloud API."""
    def __init__(self, command: Optional[str] = None):
        self.command = command or next((c for c in ("espeak-ng", "espeak", "say")
                                        if shutil.which(c)), None)

    def synthesize(self, text: str, language: str = "en", output_path: Optional[str] = None) -> TTSResult:
        if not text.strip():
            raise ValueError("TTS text must not be empty.")
        if not self.command:
            return TTSResult(False, "unavailable", True, None)
        if self.command == "say":
            args = [self.command, text]
            if output_path:
                args = [self.command, "-o", output_path, text]
        else:
            args = [self.command, "-v", language, "-w", output_path, text] if output_path else [self.command, "-v", language, text]
        subprocess.run(args, check=True, capture_output=True, text=True)
        return TTSResult(True, self.command, True, output_path)


def build_synthesizer(command: Optional[str] = None) -> SystemTTS:
    return SystemTTS(command)
