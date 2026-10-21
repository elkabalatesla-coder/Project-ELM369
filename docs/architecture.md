# Project ELM369 system architecture (live)

Updated: 2026-09-07 · Operator Spine v0.1  
Location stamp: Kokomo, Indiana 46902 USA · Joseph Michael Rose · IX JR 🌹

## Vision

Project ELM369 is Joseph Michael Rose's programming and operator stack for advanced AI, robotics/Optimus prep, computerized systems, and creative tooling — **pre-developing** designs and runnable code in one canonical GitHub repo (`elkabalatesla-coder/Project-ELM369`).

## What actually runs today

This is a **Python tools monorepo**, not a Node/Mongo microservice fiction.

| Layer | Live pieces |
|-------|-------------|
| Operator surface | `tools/elm_operator/` (Spine v0.1) — status / roster / offline / stamp / daily-dry-run |
| Health & board | `tools/elm_status/`, `tools/elm_dashboard/` (show / roster / cases) |
| Policy & provenance | `tools/elm_policy/` (geofence Kokomo 46902, English-only checks, e-sign stamp) |
| Orchestration | `tools/elm_orchestrator/` + `openapi/elm369-orchestrator.openapi.yaml` |
| Automation | `tools/elm_daily_automation/` (+ GitHub Actions schedule) |
| Memory / vault | `tools/dax_memory/`, `tools/grok_archive/`, `tools/pandora_vault/`, `vault/ELM369/…` |
| Offline | `tools/elm_offline/` (local cache; radios report `cannot_control`) |
| Decision / evolution | `tools/qbit/`, `tools/elm_evolution/` (gated; no auto prod mutation) |
| Creative / data | Liquid-3D, FLUX dry-run, tokenizer, data-finder, OMNINET, ELMDX, artifacts gallery |

## Dual identity

| Role | ID |
|------|-----|
| Primary vault / operator | `JMR08241978202646902` |
| Companion | `JMR0824197846902` |
| Session UUID | `1550e4d5-9ee3-49cd-8af8-7c9d630f84ad` |
| E-sign | Joseph Michael Rose · IX JR · 🌹 |

## Operator Spine (v0.1)

Single entrypoint for Phase-1 ops:

```bash
python3 -m tools.elm_operator status
python3 -m tools.elm_operator roster
python3 -m tools.elm_operator offline
python3 -m tools.elm_operator stamp
python3 -m tools.elm_operator daily-dry-run
```

See `docs/architecture/ELM369_OPERATOR_SPINE_v0.1.0.md`.

## Data flow (operator)

1. Operator runs Spine CLI (or dashboard/status modules directly).
2. Spine wraps existing tools — does not duplicate their logic.
3. Policy stamp / dual-ID provenance is attached on Spine envelopes.
4. Vault + daily automation persist logs under `vault/` and JSONL histories.
5. OpenAPI orchestrator remains the HTTP surface for diag/heal/optimize (gated).

## Hard holds (non-negotiable)

- Kokomo, Indiana **46902** only — no Florida-geo Google / remote-box sign-in treated as Joseph.
- No force-push; PR-only merges.
- No inventing ticket / CASE numbers (Ziggy mints cases).
- No live telephony / SMS / email send from tools (Bo drafts only).
- No live FLUX API without explicit future opt-in.
- Healing / evolution stay gated dry-run unless Joseph authorizes.

## Related docs

- `docs/STATUS.md` — registry health
- `docs/REPO_MAP.md` — tool inventory
- `docs/ELM369_IDENTITY.md` — operator identity
- `docs/architecture/ELM369_REMAINING_DESIGN_v0.1.0.md` — remaining plan
- `docs/policy/ELM369_GEOFENCE_KOKOMO_v0.1.0.md` — geofence
