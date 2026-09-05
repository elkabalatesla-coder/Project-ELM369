"""CLI for GitHub issues → vault sync."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.github_issues.sync import DEFAULT_REPO, sync


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="github-issues", description="Sync GitHub issues into ELM vault")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sync", help="Fetch open issues and ingest into vault/sources/github-issues")
    s.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)
    if args.command == "sync":
        try:
            print(json.dumps(sync(args.repo), indent=2))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
            return 1
        return 0
    return 2
