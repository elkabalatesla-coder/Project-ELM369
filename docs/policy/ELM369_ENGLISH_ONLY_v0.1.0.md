# ELM369 English-only operator policy v0.1.0

From issue [#10](https://github.com/elkabalatesla-coder/Project-ELM369/issues/10).

## Rule

Operator-facing Project ELM369 materials for `JMR08241978202646902` are authored and reviewed in **United States English**.

## Scope

- Repo docs, CLI help text, STATUS/BACKLOG, and vault operator notes
- Does **not** forbid multilingual *content* stored for translation demos (`tools/elm_translator` glossary targets)

## Enforcement (soft)

`python3 -m tools.elm_policy check-english --path docs/` scans for non-ASCII heavy files and reports; it does not delete content.
