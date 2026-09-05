# ELM369 repository map

Canonical home for Project ELM369 intent across Joseph's GitHub (`elkabalatesla-coder`).
Last updated: 2026-09-04 (round 3 — live tools).

## Active / keep

| Repo | Visibility | Role |
|------|------------|------|
| [Project-ELM369](https://github.com/elkabalatesla-coder/Project-ELM369) | public | **Only repo with real code** — vision, schemas, docs, CI, tools |

## Live tools (in this repo)

| Tool | Path | Purpose |
|------|------|---------|
| AI outage monitor | `tools/ai_outage_monitor/` | Probe AI service status pages; JSONL history |
| Daily automation | `tools/elm_daily_automation/` | Maintenance/security checklist + outage probe |
| DAX memory | `tools/dax_memory/` | Portable AI state store/recall/organize |

Scheduled: `.github/workflows/elm-daily-automation-schedule.yml` runs daily at 13:00 UTC (≈ 9am Indianapolis). Also triggerable via **Actions → workflow_dispatch**.

Quick start (from repo root):

```bash
python3 -m tools.ai_outage_monitor check --dry-run
python3 -m tools.elm_daily_automation run --dry-run
python3 -m tools.dax_memory store "note" --kind note
```

## Archived stubs (intent preserved here)

These repos were empty shells (README / LICENSE / `.gitignore` only, or templates with no product code). Archived 2026-09-04 after intent was recorded.

### Round 1

| Former repo | Intent (from README) |
|-------------|----------------------|
| `remember-me-A.I` | Always perfecting the connections of quantum memory |
| `clean-and-reorganize-and-optimize-memory.-` | Keeping Project ELM369 JMR0824197846902 memory clean / organized |
| `All-our-Logarthems-and-Algorathes-` | All logarithms and algorithms of Project ELM369 |
| `update-and-optimize-and-Organize-and-upgrade-Arctectecture` | Update, organize, optimize, and upgrade architecture |
| `New-Promting-for-Liquid-3D-and-it-s-audio-and-animation` | New prompting command line for Liquid 3D / audio / animation |
| `elkabalatesla-coder-ELM369_Qbit` | New Qbit design |

### Round 2

| Former repo | Intent (from README) |
|-------------|----------------------|
| `ELM369` | Portable AI state, DAX memory, multi-robot / auto-healing pipeline transfers |
| `ai-team-outage-monitor` | Detect, record, communicate, and recover from AI-service outages |
| `elm-daily-automation` | Daily automation: maintenance, security, optimization |
| `ELM-upgrade` | Updating ELM369 |
| `Rosey-bar-operations` | AI panel / team standards ("the bar") |
| `99-bottles-gyroscope` | Public sibling of Rosey-bar-operations |

Future work for any of these topics belongs under **Project-ELM369**, not as separate empty repositories.
