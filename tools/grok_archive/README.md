# Grok Archive Intake

Ingest Grok (and other) discussion exports into the ELM369 vault, normalize to JSONL, and extract a design/develop backlog.

## Layout

`vault/ELM369/JMR08241978202646902/sources/grok/{raw,normalized,extracted}/`

## Run

```bash
# put exports in raw/
python3 -m tools.grok_archive ingest --path vault/ELM369/JMR08241978202646902/sources/grok/raw
python3 -m tools.grok_archive list
python3 -m tools.grok_archive extract-backlog
```

Supports `.json`, `.jsonl`, and `.zip` (common Grok/X export shapes).

## Tests

```bash
python3 -m unittest discover -s tools/grok_archive/tests -v
```
