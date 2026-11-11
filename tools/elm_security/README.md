# ELM Security — Identity Resolution + Registry Scaffold

Additive security-control-plane scaffold for Project ELM369.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · canonical anchor `JMR0824197846902`

## Scope (SCAFFOLD)

| Capability | Status |
|------------|--------|
| Canonical + companion identity resolution | Present |
| Separate provenance records for both identifiers | Present |
| Security tool registry query surface | Present |
| Authorization / policy execution engine | Scaffold only |
| Destructive automation | **Never** |

## Commands

```bash
python3 -m tools.elm_security identity
python3 -m tools.elm_security tools --required-for vulnerability_prioritization
python3 -m tools.elm_security registry
python3 -m tools.elm_security verify
```

## Notes

- Canonical anchor: `JMR0824197846902`
- Companion identifier: `JMR08241978202646902`
- Merge remains forbidden unless explicitly authorized.

## Tests

```bash
python3 -m unittest tools.elm_security.tests.test_security -v
```
