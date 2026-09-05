from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.bo_assistant.draft import draft

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bo-assistant", description="Draft-only Bo replies (never sends)")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("draft")
    d.add_argument("message")
    d.add_argument("--channel", default="sms", choices=["sms","email","phone"])
    d.add_argument("--tone", default="corporate", choices=["corporate","government","both","formal"])
    args = p.parse_args(argv)
    if args.command == "draft":
        print(json.dumps(draft(args.message, channel=args.channel, tone=args.tone), indent=2)); return 0
    return 2
