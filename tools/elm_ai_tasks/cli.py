"""CLI for listing, evaluating, and running offline-first AI task contracts."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_ai_tasks.engine import evaluate, execute, list_tasks, monitor


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-ai-tasks")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List registered task contracts")

    run = sub.add_parser("run", help="Run a task after its provider has passed evaluation")
    run.add_argument("task_id")
    run.add_argument("--input-json", required=True)
    run.add_argument("--provider")
    run.add_argument("--data-classification", default="internal")
    run.add_argument("--human-approved", action="store_true")
    run.add_argument("--approval-ref")

    evaluation = sub.add_parser("evaluate", help="Run the task's registered evaluation cases")
    evaluation.add_argument("task_id")
    evaluation.add_argument("--provider")
    sub.add_parser("monitor", help="Summarize redacted local audit events")
    args = parser.parse_args(argv)

    if args.command == "list":
        result = list_tasks()
        status = 0
    elif args.command == "run":
        try:
            inputs = json.loads(args.input_json)
        except json.JSONDecodeError:
            result = {"ok": False, "error": "invalid_input_json"}
            status = 2
        else:
            result = execute(
                args.task_id,
                inputs,
                provider=args.provider,
                data_classification=args.data_classification,
                human_approved=args.human_approved,
                approval_ref=args.approval_ref,
            )
            status = 0 if result.get("ok") else 1
    elif args.command == "evaluate":
        result = evaluate(args.task_id, provider=args.provider)
        status = 0 if result.get("ok") else 1
    else:
        result = monitor()
        status = 0
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
