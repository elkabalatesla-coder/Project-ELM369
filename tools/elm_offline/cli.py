"""CLI for ELM offline snapshot cache (no radio/satellite control)."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_offline.engine import list_cached, snapshot, status, verify


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="elm-offline",
        description="Offline snapshot cache (no radio/satellite/hotspot/telephony control)",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot", help="Copy key docs/vault paths into local cache")
    sub.add_parser("status", help="Show manifest + cache metrics")
    ls = sub.add_parser("list", help="List cached files")
    ls.add_argument("-n", "--limit", type=int, default=200)
    v = sub.add_parser("verify", help="Hash-compare cache vs live sources")
    v.add_argument("-n", "--limit", type=int, default=50)
    args = p.parse_args(argv)

    if args.command == "snapshot":
        print(json.dumps(snapshot(), indent=2))
        return 0
    if args.command == "status":
        out = status()
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1
    if args.command == "list":
        print(json.dumps(list_cached(limit=args.limit), indent=2))
        return 0
    if args.command == "verify":
        out = verify(limit=args.limit)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1
    return 2
