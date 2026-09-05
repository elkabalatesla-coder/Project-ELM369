# ELM369 Daily Automation

MVP routine for Project ELM369: run maintenance / security checklists and the AI outage probe, then append a JSONL log.

## Run

From the repo root:

```bash
python3 -m tools.elm_daily_automation run --dry-run
python3 -m tools.elm_daily_automation run
```

## Config

Edit `config.json` to enable/disable tasks. Supported kinds:

- `outage_monitor` — calls `tools.ai_outage_monitor`
- `checklist` — prints/logs reminder items (no side effects)

Logs append to `data/daily_runs.jsonl`.

## Tests

```bash
python3 -m unittest discover -s tools/elm_daily_automation/tests -v
```

Additive and gated — no credential or destructive actions.
