"""CLI for OMNINET / .mo* logical namespace router."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.omninet.router import namespaces, resolve, validate


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="omninet", description="OMNINET/.mo* logical router (no mesh control)")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("resolve", help="Resolve a mo*:// URI")
    r.add_argument("uri")

    v = sub.add_parser("validate", help="Validate a mo*:// URI")
    v.add_argument("uri")

    sub.add_parser("namespaces", help="List known namespaces")

    args = p.parse_args(argv)

    if args.command == "resolve":
        out = resolve(args.uri)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1

    if args.command == "validate":
        out = validate(args.uri)
        print(json.dumps(out, indent=2))
        return 0 if out.get("valid") else 1

    if args.command == "namespaces":
        print(json.dumps(namespaces(), indent=2))
        return 0

    return 2
