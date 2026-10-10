"""QSTATE helpers for ELM369 QBIT design scaffolding."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

DEFAULT_WEIGHTS = {"L": 0.4, "M": 0.25, "R": 0.2, "H": 0.15}
_TERMS = tuple(DEFAULT_WEIGHTS)


def compute_qstate(
    L: float,
    M: float,
    R: float,
    H: float,
    weights: dict[str, float] | None = None,
) -> float:
    """QSTATE = 0.40L + 0.25M + 0.20R + 0.15H (terms clamped to 0..1)."""
    w = weights or DEFAULT_WEIGHTS

    def clamp(x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    score = (
        w["L"] * clamp(L)
        + w["M"] * clamp(M)
        + w["R"] * clamp(R)
        + w["H"] * clamp(H)
    )
    return round(score, 6)


def calibrate_weights(
    samples: Sequence[Mapping[str, Any]],
    *,
    regularization: float = 0.05,
    iterations: int = 1000,
) -> dict[str, Any]:
    """Propose QSTATE weights from expert-labeled calibration samples.

    The optimizer minimizes mean squared error plus a penalty for drifting from
    DEFAULT_WEIGHTS. It never changes the global weights or applies its result.
    """
    if (
        isinstance(samples, (str, bytes))
        or not isinstance(samples, Sequence)
        or len(samples) < len(_TERMS)
    ):
        raise ValueError("at least four calibration samples are required")
    if isinstance(regularization, bool) or not isinstance(regularization, (int, float)):
        raise ValueError("regularization must be finite and between 0 and 1000000")
    try:
        regularization = float(regularization)
    except OverflowError as exc:
        raise ValueError("regularization must be finite and between 0 and 1000000") from exc
    if not math.isfinite(regularization) or not 0 <= regularization <= 1_000_000:
        raise ValueError("regularization must be finite and between 0 and 1000000")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not 1 <= iterations <= 100_000:
        raise ValueError("iterations must be an integer from 1 to 100000")

    inputs: list[tuple[float, ...]] = []
    targets: list[float] = []
    for index, sample in enumerate(samples):
        if not isinstance(sample, Mapping):
            raise ValueError(f"sample {index} must be an object")
        terms = sample.get("terms")
        if not isinstance(terms, Mapping) or any(term not in terms for term in _TERMS):
            raise ValueError(f"sample {index} must contain L, M, R, and H terms")
        row = tuple(_calibration_value(terms[term], f"sample {index} term {term}") for term in _TERMS)
        target = _calibration_value(sample.get("target_qstate"), f"sample {index} target_qstate")
        if any(value < 0 or value > 1 for value in row) or target < 0 or target > 1:
            raise ValueError(f"sample {index} terms and target_qstate must be between 0 and 1")
        inputs.append(row)
        targets.append(target)

    weights = [DEFAULT_WEIGHTS[term] for term in _TERMS]
    baseline = tuple(weights)
    # For terms and targets in [0, 1], the MSE gradient's Lipschitz constant
    # is at most 8. This conservative step keeps projected gradient descent stable.
    step_size = 1.0 / (8.0 + 2.0 * regularization)
    count = len(inputs)
    for _ in range(iterations):
        gradient = [0.0] * len(_TERMS)
        for row, target in zip(inputs, targets):
            residual = _weighted_score(row, weights) - target
            for column, term in enumerate(row):
                gradient[column] += 2.0 * term * residual / count
        gradient = [
            delta + 2.0 * regularization * (weights[column] - baseline[column])
            for column, delta in enumerate(gradient)
        ]
        weights = _project_simplex([weight - step_size * delta for weight, delta in zip(weights, gradient)])

    baseline_scores = [_weighted_score(row, baseline) for row in inputs]
    calibrated_scores = [_weighted_score(row, weights) for row in inputs]
    return {
        "weights": {term: round(weight, 8) for term, weight in zip(_TERMS, weights)},
        "sample_count": count,
        "baseline_mae": _mae(baseline_scores, targets),
        "calibrated_mae": _mae(calibrated_scores, targets),
        "baseline_rmse": _rmse(baseline_scores, targets),
        "calibrated_rmse": _rmse(calibrated_scores, targets),
        "iterations": iterations,
        "regularization": regularization,
        "applied": False,
    }


def _calibration_value(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _project_simplex(values: Sequence[float]) -> list[float]:
    ordered = sorted(values, reverse=True)
    cumulative = 0.0
    threshold = 0.0
    for index, value in enumerate(ordered, start=1):
        cumulative += value
        candidate = (cumulative - 1.0) / index
        if value > candidate:
            threshold = candidate
    return [max(value - threshold, 0.0) for value in values]


def _weighted_score(terms: Sequence[float], weights: Sequence[float]) -> float:
    return sum(term * weight for term, weight in zip(terms, weights))


def _mae(scores: Sequence[float], targets: Sequence[float]) -> float:
    total = sum(abs(score - target) for score, target in zip(scores, targets))
    return round(total / len(targets), 8)


def _rmse(scores: Sequence[float], targets: Sequence[float]) -> float:
    squared_error = sum((score - target) ** 2 for score, target in zip(scores, targets))
    return round(math.sqrt(squared_error / len(targets)), 8)


def recommend(qstate: float, *,
              hard_block: bool = False,
              needs_authorization: bool = False) -> str:
    """Map score + hard flags to a recommendation. Score never overrides blocks."""
    if hard_block:
        return "ABORT"
    if needs_authorization:
        return "REQUEST_AUTHORIZATION"
    if qstate >= 0.85:
        return "ALLOW"
    if qstate >= 0.7:
        return "ALLOW_WITH_LIMITS"
    if qstate >= 0.5:
        return "DEFER"
    if qstate >= 0.3:
        return "MODIFY"
    return "QUARANTINE"
