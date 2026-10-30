# ELM369 Ambient Audio and Scene Adaptation Workstream
**Workstream ID:** ELM369-AUDIO-ENV-001  
**Project anchor:** JMR0824197846902  
**Companion identifier:** JMR08241978202646902 (provenance remains distinct)  
**Status:** PROPOSED / SOURCE REVIEWED / IMPLEMENTATION NOT VERIFIED  
**Created:** 2026-10-30  
**Change class:** Additive specification; no baseline mutation

## 1. Purpose and workflow placement

Add the supplied AmbientRecorderRuntime browser UI and DSP excerpt as a new workstream under the ELM369 artifact/evolution workflow. The feature is intended to provide audio capture and playback, DSP controls, a waveform/spectrum display, ambient-scene adaptation controls, and auditable runtime telemetry.

This workstream is separate from AUDIO-TX (speech-to-text/text-to-speech translation). It may later provide an audio-input adapter to AUDIO-TX, but it must not be represented as a completed STT/TTS pipeline or merged into that workstream without an explicit interface contract.

The supplied excerpt is incomplete (it ends mid-expression in the render loop) and is therefore a design/code-review input, not a buildable release artifact.

## 2. Current-state classification

| Capability | Evidence in supplied excerpt | Current classification |
|---|---|---|
| UE1 / UE2 selector | Changes a local label and telemetry text | UI simulation only; no Unreal Engine integration shown |
| Audio DSP chain | Oscillator → bass filter → low-pass → gain → analyser | Test-tone DSP path; no microphone capture |
| Recording | Toggles UI state and advances a buffer index | Simulated recording only |
| Playback | Starts a 220 Hz sawtooth oscillator | Test-tone playback only; does not replay captured audio |
| Circular buffer | Allocates a 1024-sample Float32Array | Allocated but not populated by the shown code |
| Reverse | Applies a negative oscillator frequency | Incorrect model for reverse audio playback |
| Speed | Changes oscillator frequency | Pitch change, not duration-preserving playback-rate control |
| Scene density | Slider updates displayed values and filter cutoff | Manual parameter; no ambient sensor or scene classifier shown |
| Waveform / spectrum | AnalyserNode drawing logic | Partially implemented visualization |
| Telemetry | Appends timestamped DOM entries | Basic local log; no persistence, integrity chain, or retention cap shown |
| Clock | Updates local time display | UI clock only; not a trusted audit timestamp |

## 3. Defects and engineering risks identified

1. **Broken density-meter DOM update:** document.getElementById('meterBarDensity.style.width') treats a style expression as an element ID. Resolve the meter element by its actual ID, then assign its .style.width; confirm the matching HTML element exists.
2. **No real capture source:** toggleRecord() does not request microphone permission, connect a MediaStreamAudioSourceNode, or write samples into the ring buffer.
3. **No recorded-buffer playback:** playAudio() creates a continuous oscillator. Implement playback from captured AudioBuffer/buffer data.
4. **Reverse playback is not implemented correctly:** do not use negative oscillator frequency. Reverse a copied sample buffer or use an explicitly supported reverse-playback algorithm.
5. **Speed control changes pitch:** oscillator-frequency multiplication changes pitch. Define whether the product requires varispeed or pitch-preserving time stretch; implement and label the chosen behavior accurately.
6. **Buffer lifecycle is incomplete:** define write pointer, read pointer, wrap behavior, overflow policy, channel layout, sample rate, frame count, and synchronization.
7. **Ambient density is not sensed:** until a real sensor or classifier is integrated, label this as a manual scene-density control, not an ambient sensor.
8. **Engine labels overstate integration:** UE1/UE2 are currently text/UI modes. Do not claim UnrealScript or OpenAL runtime execution without actual adapters and integration tests.
9. **Telemetry needs bounded resource use:** cap in-memory log entries, avoid unsafe dynamic HTML, and define export/persistence behavior.
10. **Lifecycle and browser handling:** handle denied microphone permission, unavailable devices, suspended AudioContext, device removal, page teardown, and unsupported browser APIs.
11. **Excerpt is truncated:** obtain the complete HTML/CSS/JavaScript source before attempting an end-to-end build or claiming syntax validation.

## 4. Target architecture

Use a layered design consistent with the ELM369 registry and evidence-gated lifecycle:

- **UI / Control Surface:** engine-mode selector, transport, DSP controls, visualization toggles, scene parameter controls, and status display.
- **Audio I/O Adapter:** explicit microphone/file input adapters; permission and device lifecycle handling.
- **DSP Graph:** source → input gain → filters/EQ → dynamics/limiter → analyser/tap → output/record path. Keep monitoring and recording paths explicit to avoid feedback loops.
- **Capture and Buffer Service:** bounded ring buffer or MediaRecorder-backed capture; metadata for sample rate, channels, timestamps, duration, and dropped frames.
- **Playback Engine:** forward/reverse buffer playback; varispeed or pitch-preserving time stretch selected by a declared mode.
- **Ambient Adaptation Service:** initially accepts a manual normalized scene-density parameter in [0,1]. Future automatic estimation must expose its source, confidence, freshness, and fallback behavior.
- **Visualization Service:** waveform, FFT spectrum, RMS, peak, clipping, and frame-rate indicators derived from actual audio samples.
- **Telemetry / Evidence Service:** structured events with event ID, UTC timestamp, monotonic sequence, component, action, result, error code, and correlation ID. Add hash-chain or registry provenance only through the established ELM369 evidence layer.
- **Runtime Adapters:** UE1/UE2 adapters remain stubs until concrete, testable engine interfaces exist.

## 5. ELM369 workflow gates

| Gate | Required evidence | Pass condition |
|---|---|---|
| G0 — Intake | Complete source, owner/provenance, intended runtime | Source completeness and provenance recorded |
| G1 — Contract | Audio I/O, buffer, DSP, playback, telemetry interfaces | Versioned schemas and explicit behavior |
| G2 — Static validation | Lint, type/syntax checks, dependency review | No unresolved blocking findings |
| G3 — Unit tests | Buffer wrap, sample conversion, gain/filter bounds, state transitions | Deterministic tests pass |
| G4 — Integration tests | Real input source, capture, playback, reverse, device loss | Tests pass with synthetic and permitted test input |
| G5 — Safety/privacy | Permission handling, no covert capture, visible recording state, retention controls | Explicit user action required to capture; clear stop/delete/export behavior |
| G6 — Performance | CPU, memory, latency, dropped-frame measurements | Measured against declared device/browser budgets |
| G7 — Evidence review | Logs, test reports, version/hash, known limitations | Evidence is inspectable and linked to artifact |
| G8 — Promotion | Human authorization and release record | No deployment claim before actual authorized deployment |

A lifecycle transition must never itself mark a gate as passed. Each pass requires its own recorded evidence. Simulation, approval, and production deployment remain distinct states.

## 6. Initial acceptance criteria

- The complete source is obtained and stored as a new versioned artifact without overwriting the submitted source.
- UI labels distinguish implemented functionality from simulated controls.
- Microphone capture starts only after an explicit user action and browser permission.
- Recording writes real samples or a real media stream; buffer duration and overflow behavior are measurable.
- Playback uses captured content, with forward/reverse behavior verified on known sample fixtures.
- Speed mode is explicit: varispeed or pitch-preserving; UI labels and tests match implementation.
- Scene-density control updates the correct meter and filter mapping, with clamped finite values.
- Waveform, spectrum, RMS, and peak values are derived from the active signal path.
- Telemetry is bounded, structured, and reports errors without claiming success prematurely.
- Tests cover denied permissions, absent devices, stop/start cycles, buffer wrap, clipping, and teardown.
- No UE1/UE2 integration claim is made until an actual engine adapter is built and tested.
- All release evidence is attached to the artifact registry and review record.

## 7. Priority sequence

**P0 — Preserve and complete intake:** archive the supplied excerpt as received; obtain the missing beginning and ending; record checksum and provenance.

**P1 — Repair the prototype:** fix the meter update, normalize state transitions, bound telemetry, and remove misleading sensor/engine labels.

**P2 — Implement real audio I/O:** microphone/file source, capture, buffer writes, playback, and error handling.

**P3 — Implement DSP and transport semantics:** gain/filter validation, forward/reverse playback, speed mode, and clipping protection.

**P4 — Integrate scene adaptation and telemetry:** manual parameter first; automatic sensing only after source/confidence/fallback contracts are defined.

**P5 — Validate and promote:** automated tests, browser/device matrix, performance evidence, privacy review, human authorization.

## 8. Scope and change-control notes

- This specification is additive to the ELM369 governance reconciliation branch and is intended for PR #154 review.
- Do not edit main, the immutable baseline, or either JMR vault path as part of this intake.
- Keep canonical and companion identifiers distinct; do not silently merge their provenance.
- Do not claim code implementation, tests, sensor integration, Unreal Engine integration, or production readiness based on this partial excerpt.
- The source supplied in the conversation is the evidence basis for the findings above. Any future external research or implementation evidence must be separately cited and versioned.
