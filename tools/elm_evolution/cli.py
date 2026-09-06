"""CLI for ELM369 controlled evolution (Joseph-gated late stages)."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_evolution.engine import advance, discover, list_changes, propose


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-evolution", description="Gated ELM369 evolution loop")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="DISCOVER repo artifacts")
    prop = sub.add_parser("propose", help="PROPOSE a change (no apply)")
    prop.add_argument("summary")
    prop.add_argument(
        "--operation",
        default="amend",
        help="amend|update|organize|optimize|upgrade|correct|repair|fix|integrate",
    )
    prop.add_argument("--artifact", default="")
    ls = sub.add_parser("list", help="List recent changes")
    ls.add_argument("-n", "--limit", type=int, default=20)
    sh = sub.add_parser("show", help="Show one change by id")
    sh.add_argument("--change-id", required=True)
    adv = sub.add_parser("advance", help="Advance one lifecycle step")
    adv.add_argument("--change-id", required=True)
    adv.add_argument("--authorize", action="store_true")
    adv.add_argument("--reject", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "discover":
        result = discover()
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    if args.command == "propose":
        print(json.dumps(propose(args.summary, operation=args.operation, artifact=args.artifact), indent=2))
        return 0

    if args.command == "list":
        print(json.dumps(list_changes(limit=args.limit), indent=2))
        return 0

    if args.command == "show":
        rows = list_changes(limit=10_000)
        match = next((r for r in rows if r.get("change_id") == args.change_id), None)
        if not match:
            print(json.dumps({"ok": False, "error": "not_found", "change_id": args.change_id}, indent=2))
            return 1
        print(json.dumps({"ok": True, "change": match}, indent=2))
        return 0

    if args.command == "advance":
        result = advance(args.change_id, authorize=args.authorize, reject=args.reject)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    return 2
