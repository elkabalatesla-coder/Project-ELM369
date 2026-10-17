"""CLI for ELM tokenizer / prompt-framework scorer."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_tokenizer.tokenize import (
    frameworks,
    resolve_priority_phrase,
    score_prompt,
    tokenize,
)


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-tokenizer", description="Tokenize + score prompt frameworks")
    sub = p.add_subparsers(dest="command", required=True)

    tok = sub.add_parser("tokenize", help="Tokenize text")
    tok.add_argument("text")

    sc = sub.add_parser("score", help="Score prompt framework coverage")
    sc.add_argument("text", nargs="?")
    sc.add_argument(
        "--phrase-priority",
        metavar="PHRASE",
        help="Resolve a known phrase spelling to its preferred form before scoring",
    )

    sub.add_parser("frameworks", help="List framework phrases + weights")

    args = p.parse_args(argv)

    if args.command == "tokenize":
        tokens = tokenize(args.text)
        print(json.dumps({"token_count": len(tokens), "tokens": tokens}, indent=2))
        return 0

    if args.command == "score":
        if args.text is not None and args.phrase_priority is not None:
            p.error("provide text either positionally or with --phrase-priority, not both")
        if args.phrase_priority is not None:
            resolution = resolve_priority_phrase(args.phrase_priority)
            result = score_prompt(resolution["resolved"])
            result["phrase_priority"] = resolution
        elif args.text is not None:
            result = score_prompt(args.text)
        else:
            p.error("score requires text or --phrase-priority PHRASE")
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "frameworks":
        print(json.dumps(frameworks(), indent=2))
        return 0

    return 2
