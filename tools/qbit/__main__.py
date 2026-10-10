"""CLI: compute QSTATE from L/M/R/H terms."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from tools.qbit import calibrate_weights, compute_qstate, recommend


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

    calibrate = sub.add_parser("calibrate", help="Propose weights from expert-labeled QSTATE samples")
    calibrate.add_argument("samples", type=Path, help="JSON file containing calibration samples")
    calibrate.add_argument("--regularization", type=float, default=0.05)
    calibrate.add_argument("--iterations", type=int, default=1000)
    calibrate.add_argument("--log", type=Path, help="Append a payload-free calibration audit record")

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
    if args.command == "calibrate":
        try:
            samples = json.loads(args.samples.read_text(encoding="utf-8"))
            if not isinstance(samples, list):
                raise ValueError("calibration file must contain a JSON array")
            result = calibrate_weights(
                samples,
                regularization=args.regularization,
                iterations=args.iterations,
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            parser.error(f"calibration failed: {exc}")
        if args.log:
            record = {
                "event": "qbit_weight_calibration",
                "created_at": datetime.now(timezone.utc).isoformat(),
                **result,
            }
            try:
                with args.log.open("a", encoding="utf-8") as log_file:
                    log_file.write(json.dumps(record, sort_keys=True) + "\n")
            except OSError as exc:
                parser.error(f"could not append calibration log: {exc}")
        print(json.dumps(result, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
