from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_operator.provenance import envelope


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="elm-operator",
        description="ELM369 Operator Spine v0.1 — Phase-1 ops facade",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Unified health report (elm_status)")
    sub.add_parser("roster", help="Grok bot roster lanes (elm_dashboard)")
    sub.add_parser("offline", help="Offline cache status (elm_offline)")
    sub.add_parser("stamp", help="Kokomo dual-ID e-sign stamp")
    sub.add_parser("daily-dry-run", help="Daily automation dry-run")

    args = p.parse_args(argv)

    if args.command == "status":
        from tools.elm_status.report import build

        report = build()
        print(json.dumps(envelope(report), indent=2, ensure_ascii=False))
        return 0 if report.get("ok") else 1

    if args.command == "roster":
        from tools.elm_dashboard.roster import roster_lanes

        print(
            json.dumps(
                envelope({"roster_lanes": roster_lanes()}),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "offline":
        from tools.elm_offline.engine import status

        out = status()
        print(json.dumps(envelope(out), indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1

    if args.command == "stamp":
        print(json.dumps(envelope(), indent=2, ensure_ascii=False))
        return 0

    if args.command == "daily-dry-run":
        from tools.elm_daily_automation.runner import run_daily

        report = run_daily(dry_run=True)
        summary = {
            "ok": report.ok,
            "dry_run": report.dry_run,
            "project_id": report.project_id,
            "started_at": report.started_at,
            "finished_at": report.finished_at,
            "results": [
                {"name": r.name, "status": r.status, "detail": r.detail}
                for r in report.results
            ],
        }
        print(json.dumps(envelope(summary), indent=2, ensure_ascii=False))
        return 0 if report.ok else 1

    return 2
