# ELM Translator — Offline Phrase Glossary (AUDIO-TX)

Issue #25. Offline English→{es,fr,de} phrase glossary for Project ELM369.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Status: SCAFFOLD

Useful for operator phrase lookup. **Not** a full audio / 100-language product.

### Remaining gap

| Capability | Status |
|------------|--------|
| Phrase glossary (en→es/fr/de) | Present |
| Batch phrase lookup | Present |
| Speech-to-text / text-to-speech | **Not implemented** (intentional for now) |
| Live neural MT API | **Not implemented** |
| SMS / phone actuation | **Never** |

## Commands

```bash
python3 -m tools.elm_translator langs
python3 -m tools.elm_translator list
python3 -m tools.elm_translator translate "hello" --to es
python3 -m tools.elm_translator batch "hello" "thank you" "vault" --to fr
```

## Tests

```bash
python3 -m unittest tools.elm_translator.tests.test_glossary -v
```
