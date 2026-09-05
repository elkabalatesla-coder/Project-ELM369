from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_status.report import build

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-status", description="Unified ELM369 health report")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("show")
    sub.add_parser("ok")
    args = p.parse_args(argv)
    report = build()
    if args.command == "show":
        print(json.dumps(report, indent=2))
        return 0 if report.get("ok") else 1
    if args.command == "ok":
        print("OK" if report.get("ok") else "NOT_OK")
        return 0 if report.get("ok") else 1
    return 2
