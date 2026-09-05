from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_translator.glossary import load, translate

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-translator")
    sub = p.add_subparsers(dest="command", required=True)
    tr = sub.add_parser("translate")
    tr.add_argument("text")
    tr.add_argument("--to", default="es")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.command == "translate":
        print(json.dumps(translate(args.text, to=args.to), indent=2, ensure_ascii=False)); return 0
    if args.command == "list":
        print(json.dumps(load(), indent=2, ensure_ascii=False)); return 0
    return 2
