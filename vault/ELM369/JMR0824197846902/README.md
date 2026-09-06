# ELM369 Vault Intake

Project: ELM369_JMR08241978202646902

Multi-source discussion archive for design/dev extraction.

## Layout

```
sources/<provider>/{raw,normalized,extracted}/
```

Providers: grok, chatgpt, claude, gemini, copilot, meta, perplexity.

## Grok Archive

Place Grok conversation exports (JSON / JSONL / ZIP from X data archive or grok.com export tools) in:

`sources/grok/raw/`

Then:

```bash
python3 -m tools.grok_archive ingest --path sources/grok/raw
python3 -m tools.grok_archive list
python3 -m tools.grok_archive extract-backlog
```
