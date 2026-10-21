# ELM369 Daily Automation

MVP routine for Project ELM369: run maintenance / security checklists and the AI outage probe, then append a JSONL log.

Also provides a read-only **last-run** helper for Ziggy’s morning ping / roster feedback bridge.

## Run

From the repo root:

```bash
python3 -m tools.elm_daily_automation run --dry-run
python3 -m tools.elm_daily_automation run
```

## Last run (Actions → roster)

```bash
python3 -m tools.elm_daily_automation last-run
python3 -m tools.elm_daily_automation last-run --json
python3 -m tools.elm_daily_automation last-run --download-log
python3 -m tools.elm_daily_automation last-run --local
```

Auth for live Actions queries (no interactive login prompts):

1. `GH_TOKEN` / `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN` in the environment
2. Else on-box PAT file at `/home/box/.config/gh/pat` (exported into the `gh` subprocess only; never printed)
3. Else already-authenticated `gh`

If Actions auth is unavailable, exit code **3** with `auth_unavailable` (falls back to local JSONL when present, labeled `source=local`).

Exit codes: `0` ok, `1` failure/attention, `2` in progress, `3` auth_unavailable, `4` no runs.

## Config

Edit `config.json` to enable/disable tasks. Supported kinds:

- `outage_monitor` — calls `tools.ai_outage_monitor`
- `checklist` — prints/logs reminder items (no side effects)
- `vault_backlog` / `github_issues_sync` / `elm_status` — see `runner.py`

Logs append to `data/daily_runs.jsonl`.

## Tests

```bash
python3 -m unittest discover -s tools/elm_daily_automation/tests -v
```

Additive and gated — no credential or destructive actions.
