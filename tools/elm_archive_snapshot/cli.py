from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_archive_snapshot.snapshot import make_snapshot

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-archive-snapshot")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("create")
    args = p.parse_args(argv)
    if args.command == "create":
        print(json.dumps(make_snapshot(), indent=2, ensure_ascii=False)); return 0
    return 2
