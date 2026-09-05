from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.pandora_vault.logs import append, sync_event, tail

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pandora-vault")
    sub = p.add_subparsers(dest="command", required=True)
    log = sub.add_parser("log")
    log.add_argument("--channel", required=True, choices=["security1", "security2", "pandora"])
    log.add_argument("--level", default="INFO")
    log.add_argument("--message", required=True)
    syn = sub.add_parser("sync")
    syn.add_argument("--message", required=True)
    syn.add_argument("--level", default="INFO")
    tl = sub.add_parser("tail")
    tl.add_argument("--channel", required=True, choices=["security1", "security2", "pandora"])
    tl.add_argument("-n", "--limit", type=int, default=20)
    args = p.parse_args(argv)
    if args.command == "log":
        print(json.dumps(append(args.channel, args.level, args.message), indent=2)); return 0
    if args.command == "sync":
        print(json.dumps(sync_event(args.message, level=args.level), indent=2)); return 0
    if args.command == "tail":
        print(json.dumps(tail(args.channel, limit=args.limit), indent=2)); return 0
    return 2
