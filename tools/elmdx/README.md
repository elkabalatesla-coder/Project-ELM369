# ELMDX — Android Diagnostics

Issue #26. Scores a **provided** inventory JSON for app risk + device posture.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE within safety bounds)

| Action | Allowed? |
|--------|----------|
| Analyze operator-supplied inventory JSON | Yes |
| Report findings / scores | Yes |
| Root device / run ADB / mutate apps | **Never** |

## Commands

```bash
python3 -m tools.elmdx sample
python3 -m tools.elmdx diagnose
python3 -m tools.elmdx diagnose --inventory path/to/inventory.json
python3 -m tools.elmdx score --inventory path/to/inventory.json
```

## Inventory shape

```json
{
  "project_id": "ELM369_JMR08241978202646902",
  "device": {"model": "...", "sdk": 34, "security_patch": "2026-01-01", "encrypted": true},
  "apps": [{"name": "com.example", "label": "App", "perms": 8, "status": "ok"}]
}
```

Statuses: `ok` | `warn` | `error` | other→`other`.

## Tests

```bash
python3 -m unittest tools.elmdx.tests.test_diagnose -v
```
