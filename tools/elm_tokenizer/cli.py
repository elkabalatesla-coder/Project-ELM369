"""CLI for ELM tokenizer / prompt-framework scorer."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_tokenizer.tokenize import frameworks, score_prompt, tokenize


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-tokenizer", description="Tokenize + score prompt frameworks")
    sub = p.add_subparsers(dest="command", required=True)

    tok = sub.add_parser("tokenize", help="Tokenize text")
    tok.add_argument("text")

    sc = sub.add_parser("score", help="Score prompt framework coverage")
    sc.add_argument("text")

    sub.add_parser("frameworks", help="List framework phrases + weights")

    args = p.parse_args(argv)

    if args.command == "tokenize":
        tokens = tokenize(args.text)
        print(json.dumps({"token_count": len(tokens), "tokens": tokens}, indent=2))
        return 0

    if args.command == "score":
        print(json.dumps(score_prompt(args.text), indent=2))
        return 0

    if args.command == "frameworks":
        print(json.dumps(frameworks(), indent=2))
        return 0

    return 2
