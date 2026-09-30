# ELM369 Remaining Design & Development Plan v0.1.0

Derived from `PROJECT_METADATA.json` and vault Grok-archive intake.
Updated: 2026-09-07 — Operator Spine v0.1 nits; AUDIO-TX aligned with PR #87.

## Status legend

- **DONE** — shipped in repo tools/
- **SCAFFOLD** — interface + CLI present; deepen next
- **PLANNED** — specified here only

## Inventory

| Component | Status | Location |
|-----------|--------|----------|
| AI outage monitor | DONE | `tools/ai_outage_monitor/` |
| Daily automation + schedule | DONE | `tools/elm_daily_automation/` + Actions |
| Vault backlog counts in daily run | DONE | `vault_backlog` task kind |
| DAX memory | DONE | `tools/dax_memory/` |
| QBIT / QSTATE | DONE | `tools/qbit/` |
| Liquid-3D prompting | DONE | `tools/liquid3d_prompting/` |
| Grok / multi-source vault intake | DONE | `vault/.../sources/*` + `tools/grok_archive/` |
| Grok inverted search index | DONE | `tools/grok_archive/` (`index` / `search`) |
| Diagnostic & Security Auditor agent | DONE | `tools/elm_orchestrator/` (`diag`) |
| Vault logger / audit trail | DONE | `tools/elm_orchestrator/` (`vault-log`) |
| Qbit self-healing engine | DONE | `tools/elm_orchestrator/` (`heal` / `heal-list` / `heal-simulate`) — QBIT-gated, dry-run only |
| Performance / O(log n) optimizer | DONE | `tools/elm_orchestrator/` (`optimize`) |
| OpenAPI orchestrator surface | DONE | `openapi/elm369-orchestrator.openapi.yaml` + `serve` |
| Geo-NTP sync | DONE | `tools/elm_orchestrator/` (`time-sync`) |
| Controlled evolution loop | DONE | `tools/elm_evolution/` (`discover`/`propose`/`advance`) |
| E-sign / watermark provenance | DONE | `tools/elm_orchestrator/` (`watermark`) — local hash watermark, not a CA |
| GitHub issues vault sync | DONE | `tools/github_issues/` + `sources/github-issues` |
| Identity / shorthand / handshake docs | DONE | `docs/ELM369_IDENTITY.md` + architecture notes |
| Toy classical obfuscate scaffold | DONE | `tools/elm_obfuscate/` |
| ELMDX inventory diagnostics | DONE | `tools/elmdx/` (JSON only — no ADB/root) |
| FLUX prompt composer | DONE | `tools/elm_flux/` (dry-run; no live API) |
| DevTools inventory | DONE | `tools/elm_devtools/` |
| OMNINET / .mo* router | DONE | `tools/omninet/` |
| Tokenizer / prompt score | DONE | `tools/elm_tokenizer/` |
| Data location finder | DONE | `tools/data_finder/` |
| Offline engine | DONE | `tools/elm_offline/` (local cache; `cannot_control` radios) |
| **Operator Spine** | **DONE** | `tools/elm_operator/` — Phase-1 ops facade (status/roster/offline/stamp/daily-dry-run) |
| Audio translator (AUDIO-TX) | DONE (offline glossary via PR #87) | `tools/elm_translator/` — phrase glossary DONE; **STT/TTS / audio pipeline / live MT remain non-goals** |
| Grok bot roster + daily ops | DONE | `docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md` |

## Still waiting on you

- A real Grok export (JSON / JSONL / ZIP) dropped into `vault/.../sources/grok/raw/` for live discussion ingest.

## Next after Spine

1. Land AUDIO-TX PR #87 (offline glossary DONE). Do **not** treat STT/TTS as remaining SCAFFOLD — those stay intentional non-goals unless Joseph/Ziggy reopen.
2. Deeper quantum / HQM + FLUX opt-in specs (architecture lane).
3. Optional console wireframe binding to Spine (design lane / Dante #96).

## Safety boundary

All scaffolds stay **additive and gated**: no credential changes, no destructive deletes, no physical actuation. Healing proposes + dry-run simulates; it does not auto-apply to production without authorization.
