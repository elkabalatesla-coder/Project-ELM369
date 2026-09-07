"""CLI for ELM369 daily automation."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.elm_daily_automation.last_run import (
    fetch_last_run,
    format_human,
    format_json,
)
from tools.elm_daily_automation.runner import run_daily


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elm-daily-automation",
        description="ELM369 daily maintenance / security / optimization routine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Execute today's configured tasks")
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Pass dry-run through to outage probe; still log checklist reminders",
    )

    last = sub.add_parser(
        "last-run",
        help="Summarize the latest scheduled daily automation Actions run (read-only)",
    )
    last.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit a single JSON object",
    )
    last.add_argument(
        "--download-log",
        action="store_true",
        help="Download elm-daily-run-log artifact and surface per-task attention",
    )
    last.add_argument(
        "--local",
        action="store_true",
        help="Prefer local data/daily_runs.jsonl (source=local)",
    )
    last.add_argument(
        "--repo",
        default=None,
        help="owner/name override (default elkabalatesla-coder/Project-ELM369)",
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        report = run_daily(dry_run=args.dry_run)
        _print_report(report)
        return 0 if report.ok else 1

    if args.command == "last-run":
        kwargs = {
            "download_log": args.download_log,
            "prefer_local": args.local,
        }
        if args.repo:
            kwargs["repo"] = args.repo
        summary = fetch_last_run(**kwargs)
        print(format_json(summary) if args.as_json else format_human(summary))
        return summary.exit_code()

    return 2


def _print_report(report) -> None:
    mode = "dry-run" if report.dry_run else "live"
    print(f"ELM369 daily automation ({mode})  project={report.project_id}")
    print(f"started  {report.started_at}")
    print(f"finished {report.finished_at}")
    print("-" * 72)
    for r in report.results:
        print(f"[{r.status:<9}] {r.name}: {r.detail}")
        for item in r.items:
            print(f"            - {item}")
    print("-" * 72)
    print("OK" if report.ok else "ATTENTION NEEDED")
