# ELM Model Training — Dry-Run Planner

Offline planning scaffold for model training and fine-tuning patterns referenced by the AI business install architecture.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope

Produces **planning records only**. It does **not** launch real training jobs, call external model providers, deploy models, or mutate production systems.

## Commands

```bash
python3 -m tools.elm_model_training catalog
python3 -m tools.elm_model_training plan "support copilot refresh" --profile rag_copilot --dataset support_faq_v3
python3 -m tools.elm_model_training list
```

## Profiles

- `rag_copilot`
- `risk_scoring`
- `forecasting`
- `recommendation`

Each plan includes lifecycle stages, guardrails, required artifacts, and evaluation requirements so future training work can stay gated and reviewable.

## Tests

```bash
python3 -m unittest tools.elm_model_training.tests.test_engine -v
```
