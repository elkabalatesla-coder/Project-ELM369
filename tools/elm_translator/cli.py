"""CLI for offline glossary translator (no audio / live MT)."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_translator.glossary import languages, load, translate, translate_many


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-translator", description="Offline phrase glossary (no audio)")
    sub = p.add_subparsers(dest="command", required=True)

    tr = sub.add_parser("translate", help="Translate one glossary phrase")
    tr.add_argument("text")
    tr.add_argument("--to", default="es")

    batch = sub.add_parser("batch", help="Translate multiple phrases (JSON list or newline file via args)")
    batch.add_argument("texts", nargs="+")
    batch.add_argument("--to", default="es")

    sub.add_parser("list", help="Dump glossary JSON")
    sub.add_parser("langs", help="List supported language codes")

    args = p.parse_args(argv)

    if args.command == "translate":
        out = translate(args.text, to=args.to)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1

    if args.command == "batch":
        out = translate_many(list(args.texts), to=args.to)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1

    if args.command == "list":
        print(json.dumps(load(), indent=2, ensure_ascii=False))
        return 0

    if args.command == "langs":
        print(json.dumps({"languages": languages(), "audio": False}, indent=2))
        return 0

    return 2
