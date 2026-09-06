# OMNINET / .mo* Protocol Router

Logical namespace router for Project ELM369 (`mo*://<namespace>[/path]`).

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE)

| Action | Allowed? |
|--------|----------|
| Resolve / validate logical URIs | Yes |
| Map namespaces to tools / roster lanes | Yes |
| Control mesh / radio / satellite / hotspot | **Never** |

## Commands

```bash
python3 -m tools.omninet namespaces
python3 -m tools.omninet resolve "mo*://vault/pandora"
python3 -m tools.omninet resolve "mo*://ziggy/CASE-20260906-001"
python3 -m tools.omninet validate "mo*://hope/tips"
```

Roster-linked namespaces include `ziggy`, `hope`, `pix`, `roster`, `daily`.

## Tests

```bash
python3 -m unittest tools.omninet.tests.test_router -v
```
