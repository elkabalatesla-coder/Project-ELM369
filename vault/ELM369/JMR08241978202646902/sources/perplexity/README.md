# Source: perplexity

Drop raw exports under `raw/`. Run:

```bash
python3 -m tools.grok_archive ingest --source perplexity --path vault/ELM369/JMR08241978202646902/sources/perplexity/raw
```

Normalized JSONL lands in `normalized/`. Extracted design/dev items in `extracted/`.
