"""CLI for ELM369 orchestrator scaffolds."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_orchestrator.agents import diagnose, heal_propose, vault_log


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-orchestrator", description="ELM369 agent scaffolds")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("diag", help="Run diagnostic presence checks")
    log = sub.add_parser("vault-log", help="Append an audit log event")
    log.add_argument("--event", required=True)
    log.add_argument("--detail", default="{}", help="JSON object string")
    heal = sub.add_parser("heal", help="Propose gated self-heal (no auto-apply)")
    heal.add_argument("--issue", required=True)

    args = parser.parse_args(argv)

    if args.command == "diag":
        result = diagnose()
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    if args.command == "vault-log":
        detail = json.loads(args.detail)
        print(json.dumps(vault_log(args.event, detail), indent=2))
        return 0

    if args.command == "heal":
        print(json.dumps(heal_propose(args.issue), indent=2))
        return 0

    return 2
