"""Deterministic ELM369 P1 intelligence primitives; standard library only."""
import hashlib
import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

def _unit(name, value):
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1 inclusive")
    return value

def qbit(evidence, confidence, impact, risk):
    """Project heuristic: E*.40 + C*.25 + I*.20 - R*.15."""
    e, c, i, r = (_unit("evidence", evidence), _unit("confidence", confidence),
                  _unit("impact", impact), _unit("risk", risk))
    return round(e * .40 + c * .25 + i * .20 - r * .15, 6)

def qstate(logic, learning, exploration, memory):
    """Weighted project state index; not a physical quantum state."""
    values = [_unit(n, v) for n, v in (
        ("logic", logic), ("learning", learning),
        ("exploration", exploration), ("memory", memory))]
    return round(sum(v*w for v, w in zip(values, (.40, .25, .20, .15))), 6)

def rolling_logic(observation, prior=None):
    """Deterministic state update; keeps source observation separate from inference."""
    if not isinstance(observation, str) or not observation.strip():
        raise ValueError("observation must be non-empty text")
    prior = prior or {}
    count = int(prior.get("observation_count", 0)) + 1
    digest = hashlib.sha256(observation.encode("utf-8")).hexdigest()
    return {
        "observation_count": count,
        "latest_observation": observation.strip(),
        "latest_observation_sha256": digest,
        "prior_state_sha256": prior.get("state_sha256"),
        "state_sha256": hashlib.sha256(
            f"{count}|{digest}|{prior.get('state_sha256', '')}".encode()
        ).hexdigest(),
        "mode": "DETERMINISTIC",
    }

def critical_thinking(claim, evidence_items=None, alternatives=None):
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("claim must be non-empty text")
    evidence_items = list(evidence_items or [])
    alternatives = list(alternatives or [])
    return {
        "claim": claim.strip(),
        "evidence_count": len(evidence_items),
        "evidence_items": evidence_items,
        "alternative_explanations": alternatives,
        "questions": [
            "What directly observable evidence supports the claim?",
            "What evidence could disconfirm it?",
            "Are the source, timestamp, and context independently verifiable?",
            "What assumptions remain untested?",
        ],
        "assessment": "INSUFFICIENT_EVIDENCE" if not evidence_items else "REVIEW_REQUIRED",
        "authorization": "NOT_GRANTED",
    }

def observable_workflow(observation, evidence=None):
    """Observe -> Understand -> Investigate; no unsupported conclusion."""
    if not isinstance(observation, str) or not observation.strip():
        raise ValueError("observation must be non-empty text")
    evidence = list(evidence or [])
    return {
        "workflow": "OCE_AOCE",
        "stages": [
            {"stage": "OBSERVE", "output": observation.strip(), "status": "RECORDED"},
            {"stage": "UNDERSTAND", "output": "Separate observed facts from assumptions.", "status": "PENDING_REVIEW"},
            {"stage": "INVESTIGATE", "output": "Collect and validate supporting or disconfirming evidence.", "status": "PENDING"},
        ],
        "evidence": evidence,
        "gate": "HUMAN_REVIEW_REQUIRED",
        "conclusion": None,
    }

def random_protocol(seed, count=1, enabled=False):
    """Explicit seeded simulation only. Disabled unless caller opts in."""
    if not enabled:
        raise PermissionError("Random Protocol is disabled by default; explicit enablement is required.")
    if seed is None:
        raise ValueError("A fixed seed is required for replayability.")
    if not 1 <= int(count) <= 10000:
        raise ValueError("count must be between 1 and 10000")
    rng = random.Random(int(seed))
    values = [rng.random() for _ in range(int(count))]
    return {
        "protocol": "SEEDED_SIMULATION",
        "seed": int(seed),
        "count": int(count),
        "values": values,
        "replayable": True,
        "cryptographic": False,
        "project_default_changed": False,
    }

def artifact_record(path):
    from pathlib import Path
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return {
        "filename": p.name,
        "size_bytes": p.stat().st_size,
        "sha256": h.hexdigest(),
        "registered_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "HASHED_NOT_EXTERNALLY_ATTESTED",
    }
