from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_artifacts.catalog import load, verify

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-artifacts")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("verify")
    args = p.parse_args(argv)
    if args.command == "list":
        data = load()
        rows = [
            {"issue": a.get("issue"), "title": a.get("title"), "kind": a.get("kind"), "runnable": a.get("runnable")}
            for a in data.get("artifacts") or []
        ]
        print(json.dumps(rows, indent=2)); return 0
    if args.command == "verify":
        v = verify()
        print(json.dumps(v, indent=2)); return 0 if v.get("ok") else 1
    return 2
