# ELM369 Evolution (SELF-OPT)

Controlled evolution loop from `ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md`.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE — gated)

Records lifecycle only. **Never** mutates production files, credentials, or physical systems.
Late stages require `--authorize`. Heal/evolution stay Joseph-gated.

Lifecycle: DISCOVERED → PROPOSED → SANDBOX → TESTING → VALIDATING → CANARY → APPROVED → DEPLOYED → MONITORED → PROMOTED.

Failure / terminal: REJECTED · QUARANTINED · ROLLED_BACK · DEPRECATED · ARCHIVED.

## Commands

```bash
python3 -m tools.elm_evolution discover
python3 -m tools.elm_evolution propose "normalize vault README links" --operation organize
python3 -m tools.elm_evolution list
python3 -m tools.elm_evolution show --change-id <id>
python3 -m tools.elm_evolution advance --change-id <id>
python3 -m tools.elm_evolution advance --change-id <id> --authorize
python3 -m tools.elm_evolution advance --change-id <id> --reject
```

## Safety

| Stage | Behavior |
|-------|----------|
| discover / propose / early advance | Allowed locally; JSONL ledger only |
| VALIDATING → CANARY → … → PROMOTED | Requires `--authorize` |
| Production file deploy | **Never performed by this tool** |
| Credential / physical / SMS / ADB | **Hard-blocked / non-goal** |

## Tests

```bash
python3 -m unittest tools.elm_evolution.tests.test_engine -v
```
