---
name: repository-orientation
description: Map Project-ELM369 structure and determine where functionality really lives. Use before changing unfamiliar areas, answering repository questions, or assessing whether a requested feature already exists.
---

# Repository orientation

1. Read `README.md` and `docs/REPO_MAP.md` first. Use the map as a starting point, not proof that a path or feature still exists.
2. Inspect the relevant module's source, README, tests, schema, configuration, and workflow. Use the registry at `data/registries/elm369_tools.json` when a tool is involved.
3. Classify evidence accurately: working implementation, test, schema, design document, artifact, or stub. A roadmap entry or completion percentage does not establish behavior.
4. Trace relevant callers and contracts before proposing an edit. Search narrowly and verify every path and symbol before relying on it.
5. If the request spans many areas, identify the smallest relevant surface and explain any unresolved ambiguity before making broad changes.
6. Report what was verified and distinguish current code from documented intent.
