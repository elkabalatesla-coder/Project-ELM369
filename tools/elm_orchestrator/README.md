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
