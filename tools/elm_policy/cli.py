from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Sequence
from tools.elm_policy.english import check_paths
from tools.elm_policy.geofence import location, stamp_line

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-policy")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("location")
    sub.add_parser("stamp")
    en = sub.add_parser("check-english")
    en.add_argument("--path", default="docs")
    args = p.parse_args(argv)
    if args.command == "location":
        print(json.dumps(location(), indent=2, ensure_ascii=False)); return 0
    if args.command == "stamp":
        print(stamp_line()); return 0
    if args.command == "check-english":
        print(json.dumps(check_paths(Path(args.path)), indent=2)); return 0
    return 2
