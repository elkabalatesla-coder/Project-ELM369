from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.data_finder.find import find

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="data-finder")
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("find")
    f.add_argument("query")
    f.add_argument("-n", "--limit", type=int, default=50)
    args = p.parse_args(argv)
    if args.command == "find":
        print(json.dumps(find(args.query, limit=args.limit), indent=2)); return 0
    return 2
