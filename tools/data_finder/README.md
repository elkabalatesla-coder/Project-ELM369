# Data Location Finder (DATA-FIND)

Find project files by name or content substring, and search the tools registry.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE)

| Action | Allowed? |
|--------|----------|
| Local filename / content search | Yes |
| Registry lookup | Yes |
| Remote crawl / Florida Google / cloud scrape | **Never** |

## Commands

```bash
python3 -m tools.data_finder find "pandora"
python3 -m tools.data_finder find "REPO_MAP" --name-only
python3 -m tools.data_finder find "geofence" --under docs -n 20
python3 -m tools.data_finder registry "OFFLINE"
```

## Tests

```bash
python3 -m unittest tools.data_finder.tests.test_find -v
```
