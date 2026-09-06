"""CLI for ELM FLUX dry-run prompt composer (no live image API)."""

from __future__ import annotations

import argparse
import json
import os
from typing import Sequence

from tools.elm_flux.compose import compose, generate_stub, list_styles


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-flux", description="FLUX prompt composer (dry-run only)")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compose", help="Compose an enriched FLUX-style prompt")
    c.add_argument("prompt")
    c.add_argument("--style", default="cyberpunk")
    c.add_argument("--aspect", default="1:1")
    c.add_argument("--negative", default="")
    c.add_argument(
        "--generate",
        action="store_true",
        help="Attempt generate path (still scaffold-gated; never calls live API)",
    )

    sub.add_parser("styles", help="List supported styles and aspects")

    args = p.parse_args(argv)

    if args.command == "styles":
        print(json.dumps(list_styles(), indent=2))
        return 0

    if args.command == "compose":
        out = compose(args.prompt, style=args.style, aspect=args.aspect, negative=args.negative)
        if args.generate:
            token = bool(os.environ.get("WAVESPEED_API_TOKEN") or os.environ.get("HF_TOKEN"))
            out = generate_stub(out, token_present=token)
        print(json.dumps(out, indent=2))
        return 0

    return 2
