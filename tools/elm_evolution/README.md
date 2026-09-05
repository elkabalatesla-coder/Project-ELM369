# ELM369 Evolution

Controlled evolution loop from `ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md`.

```bash
python3 -m tools.elm_evolution discover
python3 -m tools.elm_evolution propose "normalize vault README links" --operation organize
python3 -m tools.elm_evolution list
python3 -m tools.elm_evolution advance --change-id <id>
python3 -m tools.elm_evolution advance --change-id <id> --authorize
```

Lifecycle: DISCOVERED → PROPOSED → SANDBOX → TESTING → VALIDATING → CANARY → APPROVED → DEPLOYED → MONITORED → PROMOTED.

**Safety:** this tool records lifecycle only. It never mutates production files, credentials, or physical systems. Late stages require `--authorize`.
