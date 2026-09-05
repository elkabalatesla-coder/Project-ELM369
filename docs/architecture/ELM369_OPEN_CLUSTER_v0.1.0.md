# ELM369 Open Cluster scaffolds v0.1.0

Implements the next OPEN cluster from `docs/BACKLOG.md` without unsafe actuation.

| ID | Tool | Scope |
|----|------|-------|
| ELMDX | `tools/elmdx` | Diagnose provided Android inventory JSON |
| FLUX-UI | `tools/elm_flux` | Prompt compose; no live image API in CI |
| OMNINET | `tools/omninet` | `mo*://` logical router |
| TOKENIZER | `tools/elm_tokenizer` | Tokenize + prompt-framework score |
| DATA-FIND | `tools/data_finder` | Locate files/content in the repo |

## Explicitly not included

- Rooting / ADB mutation of phones
- Real FLUX API calls in CI
- SMS / phone dialing
- Satellite / modem / hotspot control
