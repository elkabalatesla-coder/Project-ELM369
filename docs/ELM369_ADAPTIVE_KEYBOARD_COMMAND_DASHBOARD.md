# ELM369 Adaptive Keyboard & Command Dashboard
Version: 0.1.0 · Status: design specification / prototype integration plan

## Goal
Replace dashboard toggle-only controls with a keyboard-first interaction model. A compact keyboard keeps the input field, suggestions, and emoji controls visible. Selecting a control key expands the corresponding panel; selecting it again, pressing Collapse, or pressing Escape returns to the compact layout. A registered command panel lets the user request ELM369 artifacts and tools without treating arbitrary generated text as executable code.

## UX contract
- Compact state: input + word suggestions + emoji strip + Expand / Symbols / Emoji / Options controls.
- Expanded states: `normal`, `symbols`, `emoji`, `options`, and `settings`.
- Toggle semantics: activating the currently active panel collapses it; activating a different panel switches directly to it.
- Input: suggestion tap inserts the selected token at the current selection; emoji tap inserts Unicode text; Backspace removes the prior code unit in the prototype (production must delete a full grapheme cluster); Enter submits a command only when the input starts with a recognized slash command, otherwise it preserves text.
- Accessibility: keyboard-operable controls, visible focus, accessible names, live status announcements, Escape-to-collapse, and touch targets sized for mobile.
- Device profiles: phone, tablet, Chromebook, desktop. Profiles tune layout only; they do not claim to replace the operating system keyboard.

## State model
```text
COMPACT
  Expand -> NORMAL
  Symbols -> SYMBOLS
  Emoji -> EMOJI
  Options -> OPTIONS
NORMAL | SYMBOLS | EMOJI | OPTIONS | SETTINGS
  same control / Collapse / Escape -> COMPACT
  another control -> corresponding expanded state
OPTIONS -> choose registered action -> VALIDATING -> (DENIED | NEEDS_CONFIRMATION | READY)
READY -> approved execution request -> RUNNING -> (SUCCEEDED | FAILED | TIMED_OUT)
```

## Core algorithms
1. **Panel state transition**
   `next = (activePanel == requestedPanel) ? COMPACT : requestedPanel`.
   Keep the input value and selection unchanged when switching panels.
2. **Suggestion insertion**
   Read selection range `[start,end)`; replace only that range with the chosen token; move caret to `start + token.length`; announce insertion. Production should use grapheme-aware cursor movement and locale-aware tokenization.
3. **Suggestion ranking**
   Candidate score: `S = 0.40 * recency + 0.30 * prefixMatch + 0.20 * contextFit + 0.10 * frequency`. Normalize each feature to [0,1], sort descending, and use stable lexical/id ordering for ties. Do not send typed content to a cloud service without explicit opt-in.
4. **Command resolution**
   Parse a strict command grammar, map aliases to a registry ID, reject unknown commands, and resolve only allowlisted registered artifacts. Never evaluate typed text as code, shell, SQL, or an arbitrary URL.
5. **Execution policy gate**
   Validate manifest/schema -> verify artifact identity/hash -> check capability permissions -> evaluate risk class -> request user confirmation for consequential actions -> run in a constrained sandbox -> enforce CPU/memory/time/network limits -> capture result and audit event. If any mandatory check is unknown or fails, deny or request review; do not silently proceed.
6. **Replay and audit**
   Record command ID, artifact ID/version/hash, input reference or redacted input, permission decision, confirmation, timestamps, runtime result, and event-chain hash. Use monotonic sequence numbers. A seed alone does not guarantee replay; deterministic dependencies, event order, time inputs, and runtime versions must also be controlled.
7. **Rate limiting**
   Apply per-command debounce, per-user quotas, cancellation tokens, and execution timeouts. Never debounce destructive confirmations into automatic approvals.

## Registry contract (illustrative)
```json
{
  "schema_version": "1.0",
  "command_id": "artifact.run",
  "label": "Run registered artifact",
  "artifact_id": "elm369.motion-arena.demo",
  "artifact_version": "0.1.0",
  "capabilities": ["sandbox.execute"],
  "risk_class": "low",
  "requires_confirmation": true,
  "network": "deny-by-default",
  "resource_limits": {"timeout_ms": 5000, "memory_mb": 128}
}
```
Production must validate this manifest against a versioned schema and signed/verified artifact metadata. This example is a contract sketch, not a claim that a runtime already exists.

## Suggested module boundaries
- `keyboard_state`: panel state machine and keyboard layout.
- `suggestion_engine`: tokenization, ranking, privacy policy.
- `command_parser`: grammar and alias resolution; no eval/exec.
- `artifact_registry`: immutable artifact IDs, versions, hashes, capabilities.
- `policy_gate`: authorization, risk class, confirmation requirement.
- `execution_adapter`: platform/runtime-specific sandbox interface.
- `audit_ledger`: append-only events, hashes, result summaries.
- `device_profile`: touch/keyboard dimensions and accessibility preferences.
- `platform_adapters/android`: optional Android IME service, implemented separately.
- `platform_adapters/ios`: optional custom keyboard extension; command execution remains in the containing app/runtime because iOS keyboard extensions are sandboxed and restricted.

## Platform constraints
A web dashboard can simulate an on-screen keyboard inside the app. It cannot replace the native Android/iOS system keyboard. Android requires a dedicated Input Method Editor service. iOS requires a custom keyboard extension and imposes extension restrictions; privileged artifact execution must remain in the host app or authorized backend. Chromebook/desktop should support the physical keyboard first and expose the on-screen keyboard as an optional input surface.

## Verification checklist
- [x] Standalone HTML prototype created.
- [x] JavaScript syntax check passed with Node.js.
- [x] Required UI hooks present: panel toggle, emoji, options, demo runner, device profiles.
- [ ] Browser interaction tests across mobile and desktop viewport sizes.
- [ ] Automated tests for all state transitions and selection-range insertion.
- [ ] Native Android IME and iOS extension implementation.
- [ ] Connect command registry and sandboxed runtime.
- [ ] Security review of permissions, logging, privacy, and artifact verification.

## Safety and scope
The current HTML prototype is a local demonstration. Its “Run Demo” operation is simulated and does not execute arbitrary code. No production runtime, native keyboard, or repository dashboard integration is implied until separately implemented and verified.
