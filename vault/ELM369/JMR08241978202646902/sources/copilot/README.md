# Source: copilot

Drop raw exports under `raw/`. Run:

```bash
python3 -m tools.grok_archive ingest --source copilot --path vault/ELM369/JMR08241978202646902/sources/copilot/raw
```

Normalized JSONL lands in `normalized/`. Extracted design/dev items in `extracted/`.
