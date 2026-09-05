"""QSTATE helpers for ELM369 QBIT design scaffolding."""

from __future__ import annotations

DEFAULT_WEIGHTS = {"L": 0.4, "M": 0.25, "R": 0.2, "H": 0.15}


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
