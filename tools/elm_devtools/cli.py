"""CLI for ELM system developer tools inventory."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_devtools.inventory import check_tools, list_tools


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-devtools", description="ELM369 tools inventory / health")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("inventory", help="List tools/* packages")
    sub.add_parser("check", help="Report missing README/tests/entry points")
    args = p.parse_args(argv)

    if args.command == "inventory":
        print(json.dumps(list_tools(), indent=2))
        return 0

    if args.command == "check":
        report = check_tools()
        print(json.dumps(report, indent=2))
        return 0 if report.get("ok") else 1

    return 2
