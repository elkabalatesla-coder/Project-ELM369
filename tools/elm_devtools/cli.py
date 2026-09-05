from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_devtools.inventory import list_tools

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-devtools")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("inventory")
    args = p.parse_args(argv)
    if args.command == "inventory":
        print(json.dumps(list_tools(), indent=2)); return 0
    return 2
