"""CLI for ELM369 daily automation."""

from __future__ import annotations

import argparse
from typing import Sequence

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

    args = parser.parse_args(argv)

    if args.command == "run":
        report = run_daily(dry_run=args.dry_run)
        _print_report(report)
        return 0 if report.ok else 1

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
