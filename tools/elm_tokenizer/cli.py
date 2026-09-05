from __future__ import annotations
import argparse, json
from typing import Sequence
from tools.elm_tokenizer.tokenize import score_prompt, tokenize

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-tokenizer")
    sub = p.add_subparsers(dest="command", required=True)
    tok = sub.add_parser("tokenize")
    tok.add_argument("text")
    sc = sub.add_parser("score")
    sc.add_argument("text")
    args = p.parse_args(argv)
    if args.command == "tokenize":
        print(json.dumps(tokenize(args.text), indent=2)); return 0
    if args.command == "score":
        print(json.dumps(score_prompt(args.text), indent=2)); return 0
    return 2
