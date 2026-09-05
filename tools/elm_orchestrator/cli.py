"""CLI for ELM369 orchestrator scaffolds."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_orchestrator.agents import diagnose, heal_propose, vault_log
from tools.elm_orchestrator.esign import watermark
from tools.elm_orchestrator.optimizer import suggest
from tools.elm_orchestrator.time_sync import sync_report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-orchestrator", description="ELM369 agent scaffolds")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("diag", help="Run diagnostic presence checks")
    log = sub.add_parser("vault-log", help="Append an audit log event")
    log.add_argument("--event", required=True)
    log.add_argument("--detail", default="{}", help="JSON object string")
    heal = sub.add_parser("heal", help="Propose gated self-heal (no auto-apply)")
    heal.add_argument("--issue", required=True)
    sub.add_parser("time-sync", help="Geo-NTP sync check")
    sign = sub.add_parser("watermark", help="Local provenance watermark")
    sign.add_argument("--payload", required=True, help="JSON object string")
    opt = sub.add_parser("optimize", help="Suggest logarithmic-minded optimizations")
    opt.add_argument("--workload", required=True)
    serve = sub.add_parser("serve", help="Run local OpenAPI HTTP scaffold")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8769)

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

    if args.command == "time-sync":
        report = sync_report()
        print(json.dumps(report, indent=2))
        return 0 if report.get("ok") or any(r.get("status") == "ok" for r in report.get("results", [])) else 1

    if args.command == "watermark":
        payload = json.loads(args.payload)
        print(json.dumps(watermark(payload), indent=2))
        return 0

    if args.command == "optimize":
        print(json.dumps(suggest(args.workload), indent=2))
        return 0

    if args.command == "serve":
        from tools.elm_orchestrator.server import serve as _serve

        _serve(args.host, args.port)
        return 0

    return 2
