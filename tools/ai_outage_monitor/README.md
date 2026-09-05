# AI Team Outage Monitor

MVP for Project ELM369: detect, record, and summarize outages affecting AI team services (ChatGPT, Claude, Gemini host, GitHub/Copilot host).

## Run

From the repo root:

```bash
python -m tools.ai_outage_monitor check --dry-run
python -m tools.ai_outage_monitor check
python -m tools.ai_outage_monitor report
```

## Config

Edit `config.json` to add/remove services. Kinds:

- `statuspage_v2` — Atlassian Statuspage JSON (`/api/v2/status.json`)
- `http` — plain HTTP status classification

Records append to `data/outages.jsonl` (local only; keep `.gitkeep`).

## Tests

```bash
python -m unittest discover -s tools/ai_outage_monitor/tests -v
```

Monitoring only — no credentials, no destructive actions.
