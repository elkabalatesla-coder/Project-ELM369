# ELM369 repository map

Canonical home for Project ELM369 intent across Joseph's GitHub (`elkabalatesla-coder`).
Last updated: 2026-09-04 (round 9 — backlog sweep: progress/pandora/offline/translator/bo/devtools/dashboard).

## Active / keep

| Repo | Visibility | Role |
|------|------------|------|
| [Project-ELM369](https://github.com/elkabalatesla-coder/Project-ELM369) | public | **Only repo with real code** — vision, schemas, docs, CI, tools |

## Live tools (in this repo)

| Tool | Path | Purpose | Run |
|------|------|---------|-----|
| AI outage monitor | `tools/ai_outage_monitor/` | Probe AI service status pages; JSONL history | `python3 -m tools.ai_outage_monitor check [--dry-run]` |
| Daily automation | `tools/elm_daily_automation/` | Outage probe + checklists + vault backlog counts | `python3 -m tools.elm_daily_automation run [--dry-run]` |
| DAX memory | `tools/dax_memory/` | Portable AI state store/recall/organize + indexed recall | `python3 -m tools.dax_memory irecall "…"` |
| QBIT / QSTATE | `tools/qbit/` | Decision evidence scoring (never bypasses safety) | `python3 -m tools.qbit score L M R H` |
| Liquid-3D prompting | `tools/liquid3d_prompting/` | Visual/audio/animation prompt composer | `python3 -m tools.liquid3d_prompting compose --mode visual --subject "…"` |
| Grok archive intake | `tools/grok_archive/` + `vault/.../sources/grok/` | Ingest, backlog, search, multi-source status | `python3 -m tools.grok_archive status` |
| ELM orchestrator | `tools/elm_orchestrator/` | Diag / vault-log / QBIT-gated heal / OpenAPI serve / NTP / watermark / optimize | `python3 -m tools.elm_orchestrator diag` |
| ELM evolution | `tools/elm_evolution/` | Gated DISCOVER→PROPOSE→… lifecycle (no auto prod mutation) | `python3 -m tools.elm_evolution discover` |
| GitHub issues sync | `tools/github_issues/` | Open issues → vault `sources/github-issues` | `python3 -m tools.github_issues sync` |
| Progress engine | `tools/elm_progress/` | Tool registry completion summary | `python3 -m tools.elm_progress summary` |
| Pandora / security logs | `tools/pandora_vault/` | Security Log 1/2 + Pandora vault feeds | `python3 -m tools.pandora_vault sync --message "…"` |
| Offline snapshot | `tools/elm_offline/` | Local offline cache of key docs/backlogs | `python3 -m tools.elm_offline snapshot` |
| Translator glossary | `tools/elm_translator/` | Offline phrase glossary scaffold | `python3 -m tools.elm_translator translate "hello" --to es` |
| Bo assistant | `tools/bo_assistant/` | Draft-only SMS/email/phone scripts | `python3 -m tools.bo_assistant draft "…"` |
| Devtools inventory | `tools/elm_devtools/` | List tools under tools/ | `python3 -m tools.elm_devtools inventory` |
| Dashboard board | `tools/elm_dashboard/` | JSON status board | `python3 -m tools.elm_dashboard show` |
| Toy obfuscate | `tools/elm_obfuscate/` | Classical demo obfuscation (not encryption) | `python3 -m tools.elm_obfuscate obfuscate "…"` |

### Schedules & related docs

- Daily automation schedule: `.github/workflows/elm-daily-automation-schedule.yml` (13:00 UTC ≈ 9am Indianapolis; also `workflow_dispatch`)
- Remaining design inventory: `docs/architecture/ELM369_REMAINING_DESIGN_v0.1.0.md`
- Evolution layer: `docs/architecture/ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md` + `schemas/evolution/`
- QBIT design: `docs/architecture/ELM369_QBIT_DESIGN_v0.1.0.md`
- Liquid-3D prompting: `docs/architecture/ELM369_LIQUID3D_PROMPTING_v0.1.0.md`
- Master backlog: `docs/BACKLOG.md`
- Identity: `docs/ELM369_IDENTITY.md`
- Shorthand archive: `docs/architecture/ELM369_SHORTHAND_ARCHIVE_v0.1.0.md`
- Handshake layers: `docs/architecture/ELM369_HANDSHAKE_v0.1.0.md`
- OpenAPI: `openapi/elm369-orchestrator.openapi.yaml`
- UI sketch: `Liquid3D Coloring ` (Artifact Registry React demo)

## Archived stubs (intent preserved here)

These repos were empty shells. Archived 2026-09-04 after intent was recorded.

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
