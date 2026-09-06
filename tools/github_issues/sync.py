"""Fetch GitHub issues and ingest into vault/sources/github-issues."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tools.grok_archive.ingest import ingest_path

DEFAULT_REPO = "elkabalatesla-coder/Project-ELM369"
VAULT_RAW = Path("vault/ELM369/JMR08241978202646902/sources/github-issues/raw")


def _token() -> str:
    return (
        os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        or ""
    ).strip()


def fetch_issues(
    repo: str = DEFAULT_REPO,
    *,
    state: str = "all",
    per_page: int = 100,
) -> list[dict[str, Any]]:
    """Fetch issues (not PRs). state: open | closed | all."""
    token = _token()
    if not token:
        raise RuntimeError("Set GH_TOKEN (or GITHUB_TOKEN) to sync issues")
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/repos/{repo}/issues"
            f"?state={state}&per_page={per_page}&page={page}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "ELM369-github-issues-sync",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        out.extend(i for i in data if "pull_request" not in i)
        if len(data) < per_page:
            break
        page += 1
    return out


def fetch_open_issues(repo: str = DEFAULT_REPO, *, per_page: int = 100) -> list[dict[str, Any]]:
    """Backward-compatible: open issues only."""
    return fetch_issues(repo, state="open", per_page=per_page)


def write_raw(issues: list[dict[str, Any]], raw_dir: Path | None = None) -> Path:
    dest = raw_dir or VAULT_RAW
    dest.mkdir(parents=True, exist_ok=True)
    json_path = dest / "issues.json"
    jsonl_path = dest / "issues.jsonl"
    # keep legacy filenames for older ingest paths
    legacy_json = dest / "open-issues.json"
    legacy_jsonl = dest / "open-issues.jsonl"
    slim = []
    with jsonl_path.open("w", encoding="utf-8") as fh:
        for i in issues:
            labels = [l["name"] if isinstance(l, dict) else str(l) for l in (i.get("labels") or [])]
            row = {
                "sender": "user",
                "message": f"GitHub issue #{i['number']}: {i['title']}\n\n{i.get('body') or ''}",
                "issue_number": i["number"],
                "title": i["title"],
                "url": i.get("html_url"),
                "created_at": i.get("created_at"),
                "state": i.get("state"),
                "labels": labels,
            }
            slim.append(
                {
                    "number": i["number"],
                    "title": i["title"],
                    "body": i.get("body") or "",
                    "state": i.get("state"),
                    "createdAt": i.get("created_at"),
                    "updatedAt": i.get("updated_at"),
                    "url": i.get("html_url"),
                    "labels": [{"name": n} for n in labels],
                }
            )
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    payload = json.dumps(slim, ensure_ascii=False, indent=2)
    json_path.write_text(payload, encoding="utf-8")
    legacy_json.write_text(payload, encoding="utf-8")
    legacy_jsonl.write_text(jsonl_path.read_text(encoding="utf-8"), encoding="utf-8")
    return jsonl_path


def sync(repo: str = DEFAULT_REPO, *, state: str = "all") -> dict[str, Any]:
    issues = fetch_issues(repo, state=state)
    if not issues and state == "all":
        return {"issues_fetched": 0, "skipped_ingest": True, "reason": "empty fetch; vault unchanged"}
    raw = write_raw(issues)
    stats = ingest_path(raw, source="github-issues")
    stats["issues_fetched"] = len(issues)
    return stats
