"""CLI for Data Location Finder."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.data_finder.find import find, find_registry


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="data-finder", description="Locate project files / registry entries")
    sub = p.add_subparsers(dest="command", required=True)

    f = sub.add_parser("find", help="Search files by name/content")
    f.add_argument("query")
    f.add_argument("-n", "--limit", type=int, default=50)
    f.add_argument("--name-only", action="store_true")
    f.add_argument("--under", help="Limit to a subdirectory (e.g. docs or vault)")

    r = sub.add_parser("registry", help="Search elm369_tools.json registry")
    r.add_argument("query")

    args = p.parse_args(argv)

    if args.command == "find":
        print(
            json.dumps(
                find(args.query, limit=args.limit, name_only=args.name_only, under=args.under),
                indent=2,
            )
        )
        return 0

    if args.command == "registry":
        out = find_registry(args.query)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1

    return 2
