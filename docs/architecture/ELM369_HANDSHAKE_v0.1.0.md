# ELM369 Handshake layers v0.1.0

Summarized from issue [#38](https://github.com/elkabalatesla-coder/Project-ELM369/issues/38).

## Layer model

1. **Transport** — TLS / standard crypto handshake (universal; all major platforms).
2. **Application** — OAuth / API keys (platform-defined).
3. **Operator** — ELM369 AI Panel handshake (internal): session scoped to operator `JMR08241978202646902`, logged via vault logger / audit trail, never expected to be implemented by external social platforms.

## Implementation mapping (this repo)

| Concern | Tool |
|---------|------|
| Audit / session log | `tools/elm_orchestrator` `vault-log` |
| Local provenance watermark | `tools/elm_orchestrator` `watermark` |
| Gated evolution / heal | `tools/elm_evolution`, `heal` |
| Time sync check | `tools/elm_orchestrator` `time-sync` |

External APIs still require their own TLS + credentials; ELM369 sits above that stack for operator logging and authorization gates.
