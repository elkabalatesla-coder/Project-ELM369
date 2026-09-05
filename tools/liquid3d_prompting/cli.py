"""CLI for Liquid-3D prompt composer."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.liquid3d_prompting.compose import MODES, compose, list_templates, packet_to_json


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="liquid3d-prompting",
        description="ELM369 Liquid-3D visual/audio/animation prompt composer",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compose", help="Compose a prompt packet")
    c.add_argument("--subject", required=True, help="What to depict / sound / animate")
    c.add_argument("--mode", default="visual", choices=sorted(MODES))
    c.add_argument("--tag", action="append", default=[])
    c.add_argument("--palette", action="append", default=None, help="Override palette hex (repeatable)")
    c.add_argument("--json", action="store_true", help="Emit JSON packet instead of text only")

    sub.add_parser("list-templates", help="Show template modes")

    args = parser.parse_args(argv)

    if args.command == "compose":
        packet = compose(
            args.subject,
            mode=args.mode,
            tags=args.tag,
            palette=args.palette,
        )
        if args.json:
            print(packet_to_json(packet))
        else:
            print(packet.rendered)
            print(f"\n# prompt_id={packet.prompt_id} mode={packet.mode}")
        return 0

    if args.command == "list-templates":
        for mode, text in list_templates().items():
            print(f"[{mode}]")
            print(text)
            print()
        return 0

    return 2
