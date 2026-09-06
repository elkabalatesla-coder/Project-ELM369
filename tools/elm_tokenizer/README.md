# ELM Tokenizer — Prompt Framework Scorer

Issue #27. Offline tokenize + score prompts for role/task/constraint/format/context/evaluation coverage.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE)

| Action | Allowed? |
|--------|----------|
| Tokenize text / score frameworks | Yes |
| Download model weights / call APIs | **Never** |

## Commands

```bash
python3 -m tools.elm_tokenizer frameworks
python3 -m tools.elm_tokenizer tokenize "Hello, ELM369."
python3 -m tools.elm_tokenizer score "You are a helpful analyst. Summarize in JSON only. Never leak secrets."
```

Recommendations: `ALLOW` (≥0.75) · `ALLOW_WITH_LIMITS` (≥0.45) · `MODIFY` (else).

## Tests

```bash
python3 -m unittest tools.elm_tokenizer.tests.test_tokenize -v
```
