"""CLI for ELMDX Android inventory diagnostics (no ADB/root)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.elmdx.diagnose import diagnose, load_inventory


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="elmdx",
        description="Android inventory diagnostics (JSON only — no ADB/root)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("diagnose", help="Score a provided inventory JSON")
    d.add_argument("--inventory", help="Path to device inventory JSON")

    sub.add_parser("sample", help="Print the bundled sample inventory")

    sc = sub.add_parser("score", help="Print overall score only")
    sc.add_argument("--inventory", help="Path to device inventory JSON")

    args = p.parse_args(argv)

    if args.command == "sample":
        print(json.dumps(load_inventory(), indent=2))
        return 0

    if args.command in {"diagnose", "score"}:
        inv = load_inventory(Path(args.inventory)) if getattr(args, "inventory", None) else None
        report = diagnose(inv)
        if args.command == "score":
            print(json.dumps({"overall": report["scores"]["overall"], "ok": report["ok"]}, indent=2))
        else:
            print(json.dumps(report, indent=2))
        return 0 if report.get("ok") else 1

    return 2
