from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Sequence
from tools.elmdx.diagnose import diagnose, load_inventory

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elmdx", description="Android inventory diagnostics (JSON only)")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("diagnose")
    d.add_argument("--inventory", help="Path to device inventory JSON")
    sub.add_parser("sample")
    args = p.parse_args(argv)
    if args.command == "sample":
        print(json.dumps(load_inventory(), indent=2)); return 0
    if args.command == "diagnose":
        inv = load_inventory(Path(args.inventory)) if args.inventory else None
        report = diagnose(inv)
        print(json.dumps(report, indent=2))
        return 0 if report.get("ok") else 1
    return 2
