"""Evidence-gated lifecycle transitions; no implicit deployment or promotion."""
from typing import Iterable, Optional, Set

LIFECYCLE = (
    "DISCOVER", "SNAPSHOT", "VALIDATE", "PROPOSE", "SANDBOX", "TEST",
    "VERIFY", "SECURITY_CHECK", "SAFETY_CHECK", "AUTHORIZATION",
    "CANARY", "DEPLOY", "MONITOR", "LEARN", "PROMOTE",
)
TERMINAL = {"ROLLBACK", "REJECTED"}
AUTH_REQUIRED = {"CANARY", "DEPLOY", "PROMOTE"}


class LifecycleError(ValueError):
    """Raised when a transition lacks evidence or authorization."""


def advance(current: str, *, evidence: Iterable[str] = (),
            authorized: bool = False, reject: bool = False) -> str:
    """Advance one stage only when required evidence and authorization exist."""
    if current in TERMINAL:
        raise LifecycleError("terminal_state:" + current)
    if current not in LIFECYCLE:
        raise LifecycleError("unknown_state:" + current)
    if reject:
        return "REJECTED"

    next_index = LIFECYCLE.index(current) + 1
    if next_index >= len(LIFECYCLE):
        raise LifecycleError("already_at_final_stage")
    target = LIFECYCLE[next_index]
    evidence_set: Set[str] = set(evidence)

    required = {
        "VALIDATE": {"snapshot"},
        "SANDBOX": {"proposal", "snapshot"},
        "TEST": {"sandbox"},
        "VERIFY": {"tests_passed"},
        "SECURITY_CHECK": {"verification"},
        "SAFETY_CHECK": {"security_review"},
        "AUTHORIZATION": {"safety_review"},
        "CANARY": {"authorization_record"},
        "DEPLOY": {"canary_passed"},
        "MONITOR": {"deployment_record"},
        "LEARN": {"monitoring_record"},
        "PROMOTE": {"learning_review"},
    }.get(target, set())
    missing = sorted(required - evidence_set)
    if missing:
        raise LifecycleError("missing_evidence:" + ",".join(missing))
    if target in AUTH_REQUIRED and not authorized:
        raise LifecycleError("human_authorization_required:" + target)
    return target
