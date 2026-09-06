# Offline Engine (OFFLINE)

Issue #14. Snapshots key docs, policy, backlog, sandboxes manifest, vault README paths,
Grok bot roster, and completion certificate for **local** use.

This is the **supported offline path for ELM369**.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE)

| Action | Allowed? |
|--------|----------|
| Local file snapshot / list / verify | Yes |
| Satellite / radio / hotspot / telephony control | **Never** (`cannot_control`) |

## Commands

```bash
python3 -m tools.elm_offline snapshot
python3 -m tools.elm_offline status
python3 -m tools.elm_offline list
python3 -m tools.elm_offline verify
```

## Tests

```bash
python3 -m unittest discover -s tools/elm_offline/tests -v
```
