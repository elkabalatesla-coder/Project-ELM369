---
name: elm369-tool-integration
description: Extend or connect an existing Project-ELM369 tool without duplicating capabilities or breaking its contracts. Use when changing a module under tools/ or its registry, schema, workflow, or consumers.
---

# ELM369 tool integration

1. Find the tool in `docs/REPO_MAP.md` and `data/registries/elm369_tools.json`. Inspect its module README, entry points, tests, and any schemas or workflows.
2. Confirm the tool's actual behavior from code and tests. Treat registry status, completion percentages, architecture notes, and artifacts as metadata or intent, not proof of runtime behavior.
3. Preserve the existing command/API contract and data formats unless the task explicitly changes them. Trace consumers before changing registry IDs, fields, or paths.
4. Reuse an existing tool when suitable; avoid creating a duplicate module. Keep offline and deterministic behavior where current tests and workflow require it.
5. Add focused tests for changed behavior and update the registry or repository map only when the inventory actually changes.
6. Respect each tool's safety boundary. In particular, draft-only communication, non-cryptographic obfuscation, evidence scoring, and diagnostics must not be represented as sending, encryption, authorization, or remediation.
