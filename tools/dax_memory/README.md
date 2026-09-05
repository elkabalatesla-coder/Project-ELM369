# DAX Memory

Scaffolding for Project ELM369 portable AI state / DAX memory (from archived `ELM369` + `remember-me-A.I` intents).

## Run

From the repo root:

```bash
python3 -m tools.dax_memory store "Portable AI state lives in DAX" --kind fact --tag dax
python3 -m tools.dax_memory recall "portable"
python3 -m tools.dax_memory list
python3 -m tools.dax_memory organize
python3 -m tools.dax_memory archive <memory_id>
```

Kinds: `fact`, `state`, `procedure`, `connection`, `note`.

Schema: `schemas/memory/dax_entry.schema.json`  
Store: `tools/dax_memory/data/memories.jsonl`

## Tests

```bash
python3 -m unittest discover -s tools/dax_memory/tests -v
```

Local file memory only — no credentials, no network, no destructive repo actions.
