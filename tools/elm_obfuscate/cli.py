"""CLI for toy obfuscation scaffold."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.elm_obfuscate.cipher import deobfuscate, obfuscate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elm-obfuscate",
        description="Toy classical obfuscation (NOT secure encryption)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    enc = sub.add_parser("obfuscate")
    enc.add_argument("text")
    dec = sub.add_parser("deobfuscate")
    dec.add_argument("text")
    args = parser.parse_args(argv)
    if args.command == "obfuscate":
        print(obfuscate(args.text))
        return 0
    if args.command == "deobfuscate":
        print(deobfuscate(args.text))
        return 0
    return 2
