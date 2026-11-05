"""Deterministic, simulation-only gyro-controlled matrix operations."""

from __future__ import annotations

import math
from typing import Sequence

DIMENSION = 9
MAX_ANGLE = math.pi / 4
STAGE_PAIRS = (
    ((0, 1), (3, 4), (6, 7)),
    ((1, 2), (4, 5), (7, 8)),
    ((2, 3), (5, 6), (8, 0)),
)

Matrix = tuple[tuple[float, ...], ...]


def _finite_values(values: Sequence[float], *, name: str, length: int) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or len(values) != length:
        raise ValueError(f"{name} must contain exactly {length} numeric values")

    result = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError(f"{name} values must be finite numbers")
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} values must be finite numbers") from exc
        if not math.isfinite(number):
            raise ValueError(f"{name} values must be finite numbers")
        result.append(number)
    return tuple(result)


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum(left[row][k] * right[k][column] for k in range(DIMENSION))
            for column in range(DIMENSION)
        )
        for row in range(DIMENSION)
    )


def build_matrix(
    gyro_rates: Sequence[float],
    dt: float,
    *,
    max_angle: float = MAX_ANGLE,
) -> Matrix:
    """Build a 9×9 orthogonal matrix from three gyro rates in radians/second.

    Each rate controls one three-pair butterfly stage. The integrated rates are
    bounded with tanh so arbitrary sensor values cannot create unbounded angles.
    """
    rates = _finite_values(gyro_rates, name="gyro_rates", length=3)
    (dt_value,) = _finite_values((dt,), name="dt", length=1)
    (angle_limit,) = _finite_values((max_angle,), name="max_angle", length=1)
    if dt_value <= 0:
        raise ValueError("dt must be greater than zero")
    if not 0 < angle_limit <= MAX_ANGLE:
        raise ValueError(f"max_angle must be in (0, {MAX_ANGLE}]")

    result: Matrix = tuple(
        tuple(1.0 if row == column else 0.0 for column in range(DIMENSION))
        for row in range(DIMENSION)
    )
    for rate, pairs in zip(rates, STAGE_PAIRS):
        angle = math.tanh(rate * dt_value) * angle_limit
        cosine = math.cos(angle)
        sine = math.sin(angle)
        stage = [
            [1.0 if row == column else 0.0 for column in range(DIMENSION)]
            for row in range(DIMENSION)
        ]
        for left, right in pairs:
            stage[left][left] = cosine
            stage[left][right] = -sine
            stage[right][left] = sine
            stage[right][right] = cosine
        result = _multiply(tuple(tuple(row) for row in stage), result)
    return result


def transform(matrix: Matrix, vector: Sequence[float]) -> tuple[float, ...]:
    """Apply a 9×9 matrix to a finite nine-value input vector."""
    if len(matrix) != DIMENSION or any(len(row) != DIMENSION for row in matrix):
        raise ValueError("matrix must be 9 by 9")
    matrix_values = tuple(
        _finite_values(row, name="matrix", length=DIMENSION) for row in matrix
    )
    values = _finite_values(vector, name="vector", length=DIMENSION)
    return tuple(
        sum(matrix_values[row][column] * values[column] for column in range(DIMENSION))
        for row in range(DIMENSION)
    )
