# ELM369 AI capability map and task boundary v1.0.0

## Scope

There is no finite, stable list of "all AI tools": learning approaches, application tasks, data modalities, and deployment architectures overlap and change. This map records the capabilities present in this repository and distinguishes ordinary deterministic utilities from trained-model inference. A module is not classified as an AI model merely because it is used by AI workflows.

Status meanings: **implemented** = usable local software capability; **scaffold** = composition/interface or constrained workflow without the full model-backed capability; **not present** = no corresponding inference or actuation implementation.

## Current capability inventory

| Capability | Status | Repository modules and boundary |
| --- | --- | --- |
| Language and retrieval | Implemented utilities; translation scaffold | `tools/elm_tokenizer/` scores/tokenizes prompt text; `tools/dax_memory/`, `tools/data_finder/`, and `tools/grok_archive/` provide local memory/search. `tools/elm_translator/` is a phrase glossary, not neural translation. No LLM inference or general semantic embedding search is provided by these tools. |
| Generation | Prompt/draft composition implemented; model generation not present | `tools/liquid3d_prompting/`, `tools/elm_flux/`, and `tools/bo_assistant/` compose prompts or drafts. They do not generate image, audio, video, or LLM outputs. |
| Vision | Not present | `tools/elm_flux/` prepares image prompts only. There is no image/video recognition, OCR, or vision-model inference. |
| Speech | Not present | Audio prompt composition and phrase lookup do not implement speech recognition, synthesis, or live speech translation; see `tools/elm_translator/README.md`. |
| Prediction and recommendation | Implemented deterministic rules | `tools/qbit/`, `tools/elm_orchestrator/heal.py`, `tools/elm_orchestrator/optimizer.py`, and `tools/ai_outage_monitor/classify.py` score, suggest, or classify with rules; none is a trained predictive model. |
| Analytics | Implemented deterministic reporting | `tools/elm_status/`, `tools/elm_dashboard/`, `tools/elm_progress/`, and `tools/ai_outage_monitor/` aggregate operational state. They are not predictive analytics models. |
| Agents and orchestration | Implemented constrained workflows; autonomous model agents not present | `tools/elm_orchestrator/` and `tools/elm_daily_automation/` run diagnostics, scheduled tasks, and gated proposals. They do not call an LLM or independently execute consequential actions. |
| Robotics and physical actuation | Not present | `tools/elmdx/` provides inventory diagnostics only. No robot control, sensor actuation, device mutation, or physical-world feedback loop exists. |

## Shared task contract

`data/registries/elm369_ai_tasks.json` is the versioned catalog, and `tools/elm_ai_tasks/` is the execution boundary. A task declares a stable ID, category, lifecycle/status, input and output schemas, limits, allowed data classifications, providers, evaluation requirement/cases, and consequence/approval metadata. Results have a versioned envelope with output or a stable error code and provenance (run ID, registry version, provider/model, offline status, data classification, approval attestation, lifecycle, and timestamp).

Provider adapters execute tasks only. They do not resolve OMNINET routes or choose orchestration workflows. The current `text.keyword_extract` operation is a bounded deterministic local baseline, not a trained model; its `mock` provider is only a fixture. No provider integration is enabled.

## Lifecycle controls in this slice

- Validate registry identity/uniqueness, task inputs, provider availability, output shape, size limits, and allowed data classifications.
- Require passing registered evaluation cases for the same task, provider/model, and registry version before normal runs. Evaluation results and task outcomes are observable through the local redacted audit monitor.
- Audit before provider execution, then record success/failure. Audit records deliberately exclude input/output content and approval references. If the audit cannot be written before execution, do not invoke the provider.
- Detect credential-like input field names and reject restricted-classified data. This is not comprehensive secret or personal-data detection; callers remain responsible for data minimization.
- Require a human-approval attestation and reference for consequential tasks. The library does not authenticate that attestation; production integrations must use a trusted approval service.
- Keep this implementation offline, sandboxed, and non-actuating. It has no deployment or production mutation command.

## Future expansion gate

Add a modality, task, or external provider only for a concrete use case with specified operating environment, data classification, evaluation dataset/acceptance criteria, monitoring, failure behavior, privacy and safety review, and approval/autonomy limits. Speech, vision, prediction/recommendation models, generative models, and robotics remain out of scope until such use cases are chosen.

## Research references

- [NIST AI Risk Management Framework 1.0](https://doi.org/10.6028/NIST.AI.100-1)
- [NIST Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1)
- [OECD Framework for the Classification of AI Systems](https://www.oecd-ilibrary.org/deliver/7c5f185c-en.pdf)
- [Hugging Face task catalog](https://huggingface.co/tasks)
- [scikit-learn machine-learning map](https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81228.html)

These references inform taxonomy and governance; they do not certify this repository or substitute for jurisdiction-specific legal review.
