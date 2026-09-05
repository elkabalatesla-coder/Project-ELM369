from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.omninet.router import ROUTES, resolve

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="omninet")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("resolve")
    r.add_argument("uri")
    sub.add_parser("namespaces")
    args = p.parse_args(argv)
    if args.command == "resolve":
        out = resolve(args.uri)
        print(json.dumps(out, indent=2)); return 0 if out.get("ok") else 1
    if args.command == "namespaces":
        print(json.dumps(ROUTES, indent=2)); return 0
    return 2
