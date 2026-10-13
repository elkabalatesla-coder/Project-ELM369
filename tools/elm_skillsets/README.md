# ELM Skillsets

Reusable guidance for general AI work and spelling, grammar, and proofreading.
The AI categories are informed by UNESCO's student AI competency framework and
the NIST AI Risk Management Framework. Writing guidance draws on Purdue OWL's
proofreading recommendations; source links are included in `skillsets.json`.

This catalog provides checklists for an AI workflow or human reviewer. It does
not train a model, guarantee correctness, or replace human review.

## Commands

```bash
python3 -m tools.elm_skillsets list
python3 -m tools.elm_skillsets list --category Writing
python3 -m tools.elm_skillsets show WRITING-GRAMMAR
python3 -m tools.elm_skillsets guidance AI-RESEARCH WRITING-PROOFREAD
```

## Tests

```bash
python3 -m unittest tools.elm_skillsets.tests.test_registry -v
```
