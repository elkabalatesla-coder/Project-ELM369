from __future__ import annotations
import argparse, json, os
from typing import Sequence
from tools.elm_flux.compose import compose, generate_stub

def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elm-flux")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compose")
    c.add_argument("prompt")
    c.add_argument("--style", default="cyberpunk")
    c.add_argument("--generate", action="store_true", help="Attempt generate path (still scaffold-gated)")
    args = p.parse_args(argv)
    if args.command == "compose":
        out = compose(args.prompt, style=args.style)
        if args.generate:
            token = bool(os.environ.get("WAVESPEED_API_TOKEN") or os.environ.get("HF_TOKEN"))
            out = generate_stub(out, token_present=token)
        print(json.dumps(out, indent=2)); return 0
    return 2
