# ELM369 Orchestrator Scaffolds

Agent scaffolds from `PROJECT_METADATA.json`:

- `diag` — Diagnostic & Security Auditor (presence checks)
- `vault-log` — Cryptographic Vault & Audit Logger (local JSONL)
- `heal` — Qbit Self-Healing Engine (**propose only**, never auto-apply)

```bash
python3 -m tools.elm_orchestrator diag
python3 -m tools.elm_orchestrator vault-log --event smoke --detail '{"ok":true}'
python3 -m tools.elm_orchestrator heal --issue "failing unit test in dax_memory"
```

## Extended commands

```bash
python3 -m tools.elm_orchestrator time-sync
python3 -m tools.elm_orchestrator watermark --payload '{"doc":"REPO_MAP"}'
python3 -m tools.elm_orchestrator optimize --workload "jsonl recall search"
python3 -m tools.elm_orchestrator serve --port 8769
```

OpenAPI: `openapi/elm369-orchestrator.openapi.yaml`

## Heal (QBIT-gated)

```bash
python3 -m tools.elm_orchestrator heal --issue "add missing test coverage"
python3 -m tools.elm_orchestrator heal-list
python3 -m tools.elm_orchestrator heal-simulate --proposal-id <id> --authorize
```

Simulate never mutates production files.
