# ELM DevTools — System Developer Tools

Inventory and health checks for `tools/*` packages, cross-referenced with
`data/registries/elm369_tools.json`.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE)

| Action | Allowed? |
|--------|----------|
| List tool dirs + registry status | Yes |
| Flag missing tests / README / entry | Yes |
| Mutate tools or auto-fix | **Never** |

## Commands

```bash
python3 -m tools.elm_devtools inventory
python3 -m tools.elm_devtools check
```

## Tests

```bash
python3 -m unittest tools.elm_devtools.tests.test_inventory -v
```
