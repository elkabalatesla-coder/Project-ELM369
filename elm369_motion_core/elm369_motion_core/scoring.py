"""Classical QBIT-inspired decision scoring; not quantum computation."""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class DecisionInputs:
    evidence: float
    confidence: float
    impact: float
    risk: float


@dataclass(frozen=True)
class DecisionResult:
    score: float
    accepted_by_score: bool
    risk_gate_passed: bool
    reason: str


def score_action(inputs: DecisionInputs, *, threshold: float = 0.5,
                 max_risk: float = 0.7) -> DecisionResult:
    """Score normalized [0,1] inputs; risk gate is independent of score."""
    values = (inputs.evidence, inputs.confidence, inputs.impact, inputs.risk,
              threshold, max_risk)
    if not all(isfinite(v) for v in values):
        raise ValueError("All scoring values must be finite.")
    if any(v < 0 or v > 1 for v in values):
        raise ValueError("Inputs, threshold, and max_risk must be in [0,1].")
    score = (0.40 * inputs.evidence + 0.25 * inputs.confidence
             + 0.20 * inputs.impact - 0.15 * inputs.risk)
    score_ok = score >= threshold
    risk_ok = inputs.risk <= max_risk
    if not risk_ok:
        reason = "blocked_by_risk_gate"
    elif not score_ok:
        reason = "below_score_threshold"
    else:
        reason = "score_and_risk_gates_passed"
    return DecisionResult(score, score_ok, risk_ok, reason)
