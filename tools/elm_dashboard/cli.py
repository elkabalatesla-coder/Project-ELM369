from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_dashboard.board import build
from tools.elm_dashboard.cases import summarize_case_queue
from tools.elm_dashboard.roster import roster_lanes


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="elm-dashboard",
        description="Project ELM369 AI hub JSON board (roster lanes + case queue)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show", help="Full board JSON")
    show.add_argument(
        "--no-cases",
        action="store_true",
        help="Skip case-queue filesystem scan",
    )

    sub.add_parser("roster", help="Grok bot roster lanes only")
    sub.add_parser("cases", help="Case queue summary only")

    args = p.parse_args(argv)
    if args.command == "show":
        print(
            json.dumps(
                build(include_cases=not args.no_cases),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "roster":
        print(json.dumps({"roster_lanes": roster_lanes()}, indent=2, ensure_ascii=False))
        return 0
    if args.command == "cases":
        print(json.dumps(summarize_case_queue(), indent=2, ensure_ascii=False))
        return 0
    return 2
