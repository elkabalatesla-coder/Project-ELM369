from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.bo_assistant.draft import draft, multi_turn_template


def _parse_turns(raw: str | None) -> list[dict[str, str]]:
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("--prior-turns must be a JSON array of {role, content}")
    out: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "role": str(item.get("role") or "user"),
                "content": str(item.get("content") or ""),
            }
        )
    return out


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="bo-assistant",
        description="Draft-only Bo replies (never sends SMS/email/phone)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("draft", help="Compose a draft reply (never transmits)")
    d.add_argument("message")
    d.add_argument("--channel", default="sms", choices=["sms", "email", "phone"])
    d.add_argument(
        "--tone",
        default="corporate",
        choices=["corporate", "government", "both", "formal"],
    )
    d.add_argument(
        "--prior-turns",
        default=None,
        help='JSON array of prior turns, e.g. \'[{"role":"user","content":"hi"}]\'',
    )

    mt = sub.add_parser(
        "multi-turn",
        help="Multi-turn draft template envelope (still never transmits)",
    )
    mt.add_argument("message")
    mt.add_argument("--channel", default="sms", choices=["sms", "email", "phone"])
    mt.add_argument(
        "--tone",
        default="corporate",
        choices=["corporate", "government", "both", "formal"],
    )
    mt.add_argument("--prior-turns", default=None)

    args = p.parse_args(argv)
    prior = _parse_turns(getattr(args, "prior_turns", None))
    if args.command == "draft":
        print(
            json.dumps(
                draft(args.message, channel=args.channel, tone=args.tone, prior_turns=prior),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "multi-turn":
        print(
            json.dumps(
                multi_turn_template(
                    args.message,
                    channel=args.channel,
                    tone=args.tone,
                    prior_turns=prior,
                ),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    return 2
