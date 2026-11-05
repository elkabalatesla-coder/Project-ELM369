"""Fail-closed artifact policy gate and append-only hash-chained audit ledger."""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Dict, Iterable, Optional, Set, Tuple


@dataclass(frozen=True)
class ArtifactManifest:
    artifact_id: str
    version: str
    content_sha256: str
    capabilities: Tuple[str, ...]
    risk_class: str = "low"
    network: str = "deny-by-default"
    timeout_ms: int = 5000
    memory_mb: int = 128

    def validate(self) -> Tuple[bool, str]:
        if not self.artifact_id or not self.version:
            return False, "missing artifact identity/version"
        if len(self.content_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.content_sha256):
            return False, "invalid SHA-256 digest"
        if self.risk_class not in {"low", "medium", "high", "critical"}:
            return False, "invalid risk class"
        if self.network not in {"deny-by-default", "allowlisted"}:
            return False, "invalid network policy"
        if not (1 <= self.timeout_ms <= 300000) or not (16 <= self.memory_mb <= 8192):
            return False, "resource limits outside policy bounds"
        if len(set(self.capabilities)) != len(self.capabilities):
            return False, "duplicate capability"
        return True, "manifest valid"


@dataclass(frozen=True)
class GateDecision:
    status: str  # DENIED, NEEDS_CONFIRMATION, READY
    reason: str
    artifact_id: str
    artifact_version: str


class PolicyGate:
    """Policy decision only. This class does not execute artifacts."""
    def __init__(self, granted_capabilities: Iterable[str] = (), max_risk: str = "low"):
        if max_risk not in {"low", "medium", "high", "critical"}:
            raise ValueError("invalid max_risk")
        self.granted_capabilities: Set[str] = set(granted_capabilities)
        self.max_risk = max_risk
        self._risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def evaluate(self, spec, manifest: Optional[ArtifactManifest], actual_content: Optional[bytes],
                 confirmed: bool = False) -> GateDecision:
        aid = getattr(spec, "artifact_id", "")
        version = getattr(spec, "artifact_version", "")
        def deny(reason: str) -> GateDecision:
            return GateDecision("DENIED", reason, aid, version)
        if manifest is None or actual_content is None:
            return deny("manifest or artifact content unavailable")
        valid, reason = manifest.validate()
        if not valid:
            return deny(reason)
        if manifest.artifact_id != aid or manifest.version != version:
            return deny("artifact identity/version mismatch")
        actual_hash = sha256(actual_content).hexdigest()
        if actual_hash != manifest.content_sha256:
            return deny("artifact digest mismatch")
        if manifest.capabilities != tuple(spec.capabilities):
            return deny("manifest capabilities do not match registered command")
        if any(cap not in self.granted_capabilities for cap in manifest.capabilities):
            return deny("required capability not granted")
        if self._risk_order[manifest.risk_class] > self._risk_order[self.max_risk]:
            return deny("risk class exceeds policy ceiling")
        if manifest.network != "deny-by-default":
            return deny("network access requires a separately reviewed policy")
        if spec.requires_confirmation and not confirmed:
            return GateDecision("NEEDS_CONFIRMATION", "explicit user confirmation required", aid, version)
        return GateDecision("READY", "policy checks passed; execution adapter still required", aid, version)


class AuditLedger:
    """In-memory tamper-evident event chain; production storage must be durable."""
    def __init__(self):
        self._events = []
        self._head = "0" * 64

    def append(self, event: Dict[str, object]) -> Dict[str, object]:
        seq = len(self._events) + 1
        body = {"sequence": seq, "previous_hash": self._head, "event": event}
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        record = dict(body, event_hash=digest)
        self._events.append(record)
        self._head = digest
        return dict(record)

    def verify(self) -> bool:
        previous = "0" * 64
        for index, record in enumerate(self._events, start=1):
            if record.get("sequence") != index or record.get("previous_hash") != previous:
                return False
            body = {"sequence": record["sequence"], "previous_hash": record["previous_hash"], "event": record["event"]}
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            digest = sha256(canonical.encode("utf-8")).hexdigest()
            if digest != record.get("event_hash"):
                return False
            previous = digest
        return True

    def events(self):
        return tuple(dict(event) for event in self._events)
