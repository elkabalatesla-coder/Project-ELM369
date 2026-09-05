"""CLI for AI Team Outage Monitor."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.ai_outage_monitor.check import read_recent, run_checks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-outage-monitor", description="ELM369 AI team outage monitor"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Probe configured AI services")
    check.add_argument(
        "--dry-run", action="store_true", help="Skip network; emit synthetic ok results"
    )

    report = sub.add_parser("report", help="Show recent JSONL records")
    report.add_argument(
        "-n", "--limit", type=int, default=20, help="How many recent rows (default 20)"
    )

    args = parser.parse_args(argv)

    if args.command == "check":
        results = run_checks(dry_run=args.dry_run)
        _print_table(results)
        bad = [r for r in results if r.status in {"down", "degraded", "unknown"}]
        return 1 if bad and not args.dry_run else 0

    if args.command == "report":
        rows = read_recent(limit=args.limit)
        if not rows:
            print("No records yet. Run: python -m tools.ai_outage_monitor check")
            return 0
        for row in rows:
            print(
                f"{row.get('checked_at', '?'):<28} {row.get('service_id', '?'):<16} "
                f"{row.get('status', '?'):<10} {row.get('detail', '')}"
            )
        return 0

    return 2


def _print_table(results) -> None:
    print(f"{'SERVICE':<28} {'STATUS':<10} {'HTTP':<6} DETAIL")
    print("-" * 72)
    for r in results:
        http = "-" if r.http_status is None else str(r.http_status)
        print(f"{r.name:<28} {r.status:<10} {http:<6} {r.detail}")
