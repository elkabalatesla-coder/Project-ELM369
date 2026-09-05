from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_progress.engine import load_registry, summarize, verify_paths

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-progress")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")
    sub.add_parser("verify")
    ls = sub.add_parser("list")
    ls.add_argument("--status")
    args = p.parse_args(argv)
    if args.command == "summary":
        print(json.dumps(summarize(), indent=2)); return 0
    if args.command == "verify":
        print(json.dumps(verify_paths(), indent=2)); return 0
    if args.command == "list":
        tools = load_registry().get("tools") or []
        if args.status:
            tools = [t for t in tools if t.get("status")==args.status]
        print(json.dumps(tools, indent=2)); return 0
    return 2
