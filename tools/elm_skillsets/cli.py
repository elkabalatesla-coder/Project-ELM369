"""Command-line interface for AI and writing skill guidance."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_skillsets.registry import get_skillset, get_skillsets, render_guidance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-skillsets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser("list", help="List available skillsets")
    listing.add_argument("--category", help="Filter by category, such as AI or Writing")

    show = subparsers.add_parser("show", help="Show one skillset")
    show.add_argument("skill_id")

    guidance = subparsers.add_parser("guidance", help="Render one or more guidance checklists")
    guidance.add_argument("skill_ids", nargs="+")

    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            result = get_skillsets(args.category)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "show":
            print(json.dumps(get_skillset(args.skill_id), ensure_ascii=False, indent=2))
        else:
            print(render_guidance(args.skill_ids))
    except KeyError as error:
        parser.error(str(error))
    return 0
