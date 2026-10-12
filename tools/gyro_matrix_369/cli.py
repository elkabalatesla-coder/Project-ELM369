"""CLI for the simulation-only gyro matrix."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.gyro_matrix_369.matrix import build_matrix


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a simulation-only 3/6/9 gyro matrix")
    parser.add_argument("gyro_x", type=float, help="X angular rate in radians/second")
    parser.add_argument("gyro_y", type=float, help="Y angular rate in radians/second")
    parser.add_argument("gyro_z", type=float, help="Z angular rate in radians/second")
    parser.add_argument("--dt", type=float, required=True, help="sample interval in seconds")
    args = parser.parse_args(argv)
    matrix = build_matrix((args.gyro_x, args.gyro_y, args.gyro_z), args.dt)
    print(json.dumps({"dimension": 9, "matrix": matrix, "physical_actuation": False}, indent=2))
    return 0
