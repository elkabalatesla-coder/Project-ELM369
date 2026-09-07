# ELM Translator — Offline Phrase Glossary (AUDIO-TX)

Issue #25. Offline English→{es,fr,de} phrase glossary for Project ELM369.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Status: DONE (offline phrase tool)

Honest scope: operator/ELM **phrase glossary** with fuzzy suggestions, coverage, and search.  
**Not** a full audio / 100-language product.

### Capabilities

| Capability | Status |
|------------|--------|
| Phrase glossary (en→es/fr/de) | **DONE** (expanded operator/ELM set) |
| Batch phrase lookup | **DONE** |
| Fuzzy / suggest-nearest on exact miss | **DONE** (stdlib `difflib`) |
| Coverage / status CLI | **DONE** |
| Substring search CLI | **DONE** |
| Speech-to-text / text-to-speech | **Not implemented** (intentional non-goal) |
| Live neural MT API | **Not implemented** (intentional non-goal) |
| Audio capture / playback pipeline | **Not implemented** (intentional non-goal) |
| SMS / phone actuation | **Never** |

## Commands

```bash
python3 -m tools.elm_translator langs
python3 -m tools.elm_translator list
python3 -m tools.elm_translator translate "hello" --to es
python3 -m tools.elm_translator batch "hello" "thank you" "vault" --to fr
python3 -m tools.elm_translator search vault
python3 -m tools.elm_translator coverage
python3 -m tools.elm_translator status
```

Exact miss returns `suggestions` (nearest English phrases).

## Tests

```bash
python3 -m unittest tools.elm_translator.tests.test_glossary -v
```
