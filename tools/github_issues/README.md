# GitHub issues → vault

```bash
export GH_TOKEN=…   # classic PAT with repo scope
python3 -m tools.github_issues sync
```

Writes `vault/.../sources/github-issues/raw/`, then runs the shared grok_archive ingest/normalize/backlog/index pipeline for source `github-issues`.
