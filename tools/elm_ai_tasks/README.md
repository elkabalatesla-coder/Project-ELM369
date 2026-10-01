# ELM369 AI task contracts

This is an offline-first task execution slice. It is separate from OMNINET's logical URI resolution and the orchestrator's workflow decisions. The built-in providers do not load models or call external services; any provider registered by an embedding application is its responsibility.

## Current task

`text.keyword_extract` is a deterministic keyword-frequency baseline, not a trained AI model. It accepts an internal/public text input, returns a keyword list, and supports `builtin_rules` and a fixed-output `mock` provider. The registry is at `data/registries/elm369_ai_tasks.json`.

## Lifecycle and data controls

- Run the registered synthetic evaluations before each provider/registry-version pair is used. Only a passing evaluation permits execution.
- Inputs are schema-checked, capped at 8,192 characters, reject restricted data and sensitive credential-like field names, and are never copied into the audit log. This is not general PII or secret detection; callers must minimize and classify data before submitting it.
- Audit records include task/provider/model, registry version, mode, outcome, timestamp, and run ID; they intentionally omit payloads, outputs, and approval references. The monitor summarizes these records.
- Consequential tasks require both `human_approved` and a nonempty `approval_ref` for evaluation and execution. This API records an operator attestation, not an authenticated identity or authorization; a production caller must connect it to a trusted approval system. Current registered task is non-consequential.
- Tasks default to sandbox lifecycle. There is no deployment, file mutation, external provider, or physical actuation path.

## Commands

```bash
python3 -m tools.elm_ai_tasks list
python3 -m tools.elm_ai_tasks evaluate text.keyword_extract
python3 -m tools.elm_ai_tasks run text.keyword_extract --input-json '{"text":"alpha beta alpha"}'
python3 -m tools.elm_ai_tasks monitor
python3 -m unittest discover -s tools/elm_ai_tasks/tests -v
```

For consequential tasks, both `evaluate` and `run` require `--human-approved --approval-ref <reference>`; this is an operator attestation, not authenticated authorization.

`run` uses an append-only local log at `tools/elm_ai_tasks/data/runs.jsonl`; provide `audit_path` to the Python API to isolate tests or deployments. `mock` is a deterministic test adapter and is not evidence of model quality.
