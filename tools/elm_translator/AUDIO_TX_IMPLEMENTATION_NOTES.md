# AUDIO-TX implementation notes

This adds orchestration interfaces and explicit offline fallbacks. It does not bundle a speech-recognition model or a speech-synthesis engine.

- STT accepts an injected local recognizer. If absent or unsuccessful, it reads a UTF-8 transcript sidecar. Without either, it raises a clear error.
- Translation reuses the existing offline phrase glossary; unknown phrases remain unknown and are not fabricated.
- TTS accepts an injected local synthesizer. If absent, it saves translated text as a .txt file and reports audio_generated=false.
- These modules perform no network calls.
- No SMS, phone, telephony, radio, or external actuation is performed.
- Output includes the existing project watermark and project identifier from the glossary layer.

## Verification

Run:

    python3 -m unittest tools.elm_translator.tests.test_audio_pipeline -v
    python3 -m unittest tools.elm_translator.tests.test_glossary -v

## Remaining work before calling AUDIO-TX a full audio feature

1. Select and package supported offline STT/TTS backends for target platforms.
2. Add real audio fixture tests under an approved license.
3. Validate supported audio formats, duration limits, and file-size limits.
4. Add language/voice mapping and glossary-preservation tests for phrases and named entities.
5. Measure accuracy, latency, and memory usage on Android/Termux and Chromebook environments.
6. Update the registry only after backend tests pass.
