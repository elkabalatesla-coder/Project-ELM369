# Project-ELM369
Visioning advanced Technology of Today and the future and pre-developing programming code for it in advance and coming up with our own intellectual designs

## Dual Magic QBIT v1.1.0 prototype

The standard-library Python tool `tools.elm369_dual_magic` provides an offline,
rule-based answer engine, a Source Registry, and a Question Learning Engine.
This version identifies the Dual Magic prototype, not the entire repository.
The existing `tools.qbit` QSTATE scoring API and CLI are unchanged.
Python 3.8+ is supported; no additional dependencies are required.

```python
from tools.elm369_dual_magic import (
    ELM369DualMagicQBIT, Evidence, LearningEvent, Mode,
    QuestionLearningEngine, SourceRecord, SourceRegistry,
)

registry = SourceRegistry()
registry.register(SourceRecord(
    "s1", "Example report", "https://example.org/report", "secondary",
    "reviewer", "2026-10-18T00:00:00Z",
))
engine = ELM369DualMagicQBIT(seed=42)
exploration = engine.ask("Is this claim true?", Mode.RANDOM)
answer = engine.ask(
    "Is this claim true?",
    evidence=[Evidence("s1", "An observation about this claim", True)],
)
assert answer.answer_kind == "insufficient_evidence"  # Not verified by the caller.
learning = QuestionLearningEngine()
learning.record(LearningEvent(
    answer.question, answer.answer, answer.answer_kind, "Need more context",
    "evidence", answer.timestamp_utc,
))
print(learning.suggest_follow_up("evidence"))
print(registry.export_json())
print(registry.digest())
```

### Scope and trust boundary

- **Random mode** selects exploratory prompts, not evidence or predictions.
  Even “My sources say no” in this mode is a random prompt: inspect `mode`,
  `answer_kind`, and `rationale`, not just the answer text.
- **Evidence mode** evaluates caller-supplied `Evidence` support flags.
  Only `verified=True` items with a boolean `supports` value affect the
  conclusion. No such evidence means unknown, not “no”; opposing flags
  produce a conflict, not a majority vote. `supports=None` is non-directional.
  Only a trusted external review process should set `Evidence.verified=True`.
  The engine cannot determine authenticity, relevance, completeness, or truth.
- Question classification is heuristic, not a general language parser.
  Loaded and self-referential questions receive premise/logical prompts;
  ambiguous and compound questions request clarification. Open questions also
  request a scoped proposition rather than forcing a yes/no answer.
- The **Source Registry** stores source IDs, titles, URIs, authority/owner
  labels, check/expiry timestamps, verification metadata, and notes.
  Nonblank IDs are exact, case-sensitive strings; duplicates are rejected
  without overwriting. `get()` raises `KeyError` for unknown IDs.
  Registration does not fetch URLs, authenticate ownership, verify claims,
  validate timestamps, or enforce expiry. `Evidence.source` may reference a
  registry ID, but lookup, freshness review, and linking are the caller's
  responsibility. Registry verification metadata never promotes evidence.
- The **Question Learning Engine** stores immutable feedback observations in
  insertion order and suggests predefined follow-ups by skill tag (with a
  generic fallback). It does not train a model, rewrite answers, verify
  evidence, or turn feedback/preferences into proof.
- Registry records and feedback are in memory, isolated per instance.
  JSON exports are snapshots, not automatic persistence; no import/reload
  API is provided. No network calls or repository mutations are performed.
- Confidence values are fixed rule-based labels, **not calibrated probabilities**
  or independent estimates of truth.

### Provenance and verification

Answer records include the original/normalized question, mode, classification,
answer, rationale, supplied evidence (including ignored evidence), algorithm
version, UTC timestamp, and `record_sha256`.
The digest hashes all record fields **except `record_sha256` itself**.
Registry snapshots are sorted by `source_id`; feedback snapshots retain event
order. Their digests hash the complete exported arrays after canonicalization:
`json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`,
encoded as UTF-8, then SHA-256. Pretty-printed export bytes are not canonical.
Answer timestamps are part of the hash, so repeated answers need not hash alike.

Digests detect changes only against a separately preserved trusted digest.
They are not signatures and prove neither authenticity, authorship, ownership,
nor factual correctness. Answer records are mutable snapshots; their stored
digest does not automatically update after mutation.

Run the prototype and existing QSTATE regression suites from the repository root:

```bash
python -m unittest discover -s tools/elm369_dual_magic/tests -v
python -m unittest discover -s tools/qbit/tests -v
```

Category / Subcomponent                        Completion
──────────────────────────────────────────────────────────────
1. Available Technologies & Facts Today
   ├─ Quantum Computing Milestones              ██████████ 100%
   ├─ VR/AR & 3D/4D Graph System               █████████  90%
   ├─ Liquid3D Framework & Algorithms          █████████  90%
   └─ Forward & Backward Chaining              █████████  90%

2. Not There Yet
   ├─ Multi-Loop Engine Structure              ███████    70%
   ├─ Astral Plane / Metaphysical Integration  █████      50%
   └─ Futuristic Prototyping                   ████       30%

3. Transitional (Could Be Now / Needs Time)
   ├─ Random Protocol & Quantum Curvature      ███████    60%
   ├─ Sandbox for Artifacts & Algorithm Testing ██████████ 100%
   └─ Rolling Logic & Forward/Backward Chaining ███████  60%

4. Random Protocol Surprises
   ├─ Surprise Artifacts Generation            ████████   80%
   └─ Integration into Main Datasets           ████████   80%
──────────────────────────────────────────────────────────────
Overall Weighted Completion: ~70%


---

Owner: Joseph Michael Rose
D.O.B.: 08/24/1978
Location: Kokomo, Indiana 46902 (Eastern Standard Time)
Timestamps:
- ISO 8601 (commit time): [to be filled at commit, e.g. 2026-07-30T13:07:23-05:00]
- Human-friendly (commit time): [to be filled at commit, e.g. July 30, 2026 1:07 PM EST]
E-signature: Esign Joseph Michael Rose
Eintial: Eintial IX JR
E-Symbol: 🌹
