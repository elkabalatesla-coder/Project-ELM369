"""CLI: compute QSTATE from L/M/R/H terms."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.qbit import compute_qstate, recommend


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qbit", description="ELM369 QBIT / QSTATE helpers")
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="Compute QSTATE from L M R H")
    score.add_argument("L", type=float)
    score.add_argument("M", type=float)
    score.add_argument("R", type=float)
    score.add_argument("H", type=float)
    score.add_argument("--hard-block", action="store_true")
    score.add_argument("--needs-authorization", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "score":
        q = compute_qstate(args.L, args.M, args.R, args.H)
        rec = recommend(
            q,
            hard_block=args.hard_block,
            needs_authorization=args.needs_authorization,
        )
        print(f"QSTATE={q}")
        print(f"recommendation={rec}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
