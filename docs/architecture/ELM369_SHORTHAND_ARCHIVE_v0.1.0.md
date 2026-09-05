# ELM369 Shorthand Archive v0.1.0

From issue [#45](https://github.com/elkabalatesla-coder/Project-ELM369/issues/45) (`ELM369-ARCH-0416A`).

## Intent

Long-form discussions are hard to track/quote. Convert them into structured compressed micro-records that stay searchable.

## Pipeline (live)

| Stage | Tool |
|-------|------|
| Raw export drop | `vault/.../sources/<provider>/raw/` |
| Normalize + backlog extract | `python3 -m tools.grok_archive ingest --path … --source <provider>` |
| Search | `python3 -m tools.grok_archive search "…"` |
| GitHub issues as discussions | `python3 -m tools.github_issues sync` |
| Daily backlog counts | `elm_daily_automation` `vault_backlog` task |

## Micro-record shape

Normalized JSONL rows carry `record_id`, `source`, `role`, `content`, timestamps, plus issue metadata when present (`issue_number`, `title`, `url`).
