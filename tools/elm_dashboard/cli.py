from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_dashboard.board import build

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-dashboard")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("show")
    args = p.parse_args(argv)
    if args.command == "show":
        print(json.dumps(build(), indent=2)); return 0
    return 2
