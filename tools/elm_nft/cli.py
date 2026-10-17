"""Create, plan, generate, and verify offline NFT asset collections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.elm_nft.engine import generate, plan, read_config, verify

EXAMPLE = Path(__file__).with_name("example.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elm-nft", description="Offline NFT artwork and metadata; no minting or wallets")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create an editable collection configuration")
    init.add_argument("config", type=Path)
    planning = sub.add_parser("plan", help="Validate configuration and report capacity/tasks")
    planning.add_argument("config", type=Path)
    gen = sub.add_parser("generate", help="Generate a fresh collection directory")
    gen.add_argument("config", type=Path)
    gen.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("verify", help="Verify collection file integrity, not authenticity")
    check.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            with args.config.open("xb") as handle:
                handle.write(EXAMPLE.read_bytes())
            result = {"ok": True, "config": str(args.config)}
        elif args.command == "plan":
            result = {"ok": True, **plan(read_config(args.config))}
        elif args.command == "generate":
            result = generate(read_config(args.config), args.output)
        else:
            result = verify(args.output)
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1
