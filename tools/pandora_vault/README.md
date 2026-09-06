# Pandora Vault / Security Logs

Local **Security Log 1**, **Security Log 2**, and **Pandora Vault** JSONL feeds
(from issues #11 / #29). Offline-only — no remote exfiltration.

- Project / primary vault: `ELM369_JMR08241978202646902`
- Companion vault: `JMR0824197846902`
- E-sign stamp: Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902

## Commands

```bash
# Fan-out write to security1 + security2 + pandora
python3 -m tools.pandora_vault sync --message "vault sync check"

# Single-channel append (WARN/ERROR/CRITICAL/VAULT also mirror into pandora)
python3 -m tools.pandora_vault log --channel security1 --level WARN --message "attention"

# Tail recent rows
python3 -m tools.pandora_vault tail --channel pandora -n 10

# Channel stats
python3 -m tools.pandora_vault stats
```

## Data paths

| Channel | File |
|---------|------|
| security1 | `tools/pandora_vault/data/security-log-1.jsonl` |
| security2 | `tools/pandora_vault/data/security-log-2.jsonl` |
| pandora | `tools/pandora_vault/data/pandora-vault.jsonl` |

## Safety

- Local append/tail only
- Heal / mutation stays propose/dry-run elsewhere
- Filing / external disclosure remains Joseph-gated

## Tests

```bash
python3 -m unittest tools.pandora_vault.tests.test_logs -v
```
