from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_offline.engine import snapshot, status

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-offline", description="Offline snapshot cache (no radio/satellite control)")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    sub.add_parser("status")
    args = p.parse_args(argv)
    if args.command == "snapshot":
        print(json.dumps(snapshot(), indent=2)); return 0
    if args.command == "status":
        print(json.dumps(status(), indent=2)); return 0
    return 2
