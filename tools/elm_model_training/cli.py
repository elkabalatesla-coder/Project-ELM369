"""CLI for dry-run ELM369 model training planning."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_model_training.engine import catalog, list_plans, plan


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-model-training", description="Dry-run model training planner")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog", help="Show supported model training profiles")
    make = sub.add_parser("plan", help="Create a dry-run model training plan")
    make.add_argument("objective")
    make.add_argument("--profile", default="rag_copilot")
    make.add_argument("--dataset", default="unspecified")
    make.add_argument("--mode", default="")
    make.add_argument("--owner", default="ai_product_owner")
    make.add_argument("--risk-tier", default="")

    ls = sub.add_parser("list", help="List recent model training plans")
    ls.add_argument("-n", "--limit", type=int, default=20)

    args = parser.parse_args(argv)

    if args.command == "catalog":
        print(json.dumps(catalog(), indent=2, ensure_ascii=False))
        return 0

    if args.command == "plan":
        result = plan(
            args.objective,
            profile=args.profile,
            dataset=args.dataset,
            mode=args.mode or None,
            owner=args.owner,
            risk_tier=args.risk_tier or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    if args.command == "list":
        print(json.dumps(list_plans(limit=args.limit), indent=2, ensure_ascii=False))
        return 0

    return 2
