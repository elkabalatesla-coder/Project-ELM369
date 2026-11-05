"""Command orchestration boundary for an ELM369 adaptive keyboard UI.

This service returns decisions/results for a UI adapter. It never executes generated code.
"""
from typing import Optional
from .policy_gate import ArtifactManifest, AuditLedger, PolicyGate
from .registry import CommandRegistry, default_registry


class KeyboardCommandService:
    def __init__(self, registry: Optional[CommandRegistry] = None,
                 gate: Optional[PolicyGate] = None, ledger: Optional[AuditLedger] = None):
        self.registry = registry or default_registry()
        self.gate = gate or PolicyGate()
        self.ledger = ledger or AuditLedger()

    def request(self, raw_command: str, manifest: Optional[ArtifactManifest] = None,
                artifact_content: Optional[bytes] = None, confirmed: bool = False) -> dict:
        spec = self.registry.resolve(raw_command)
        if spec is None:
            result = {"status": "DENIED", "reason": "unknown or disabled command"}
            self.ledger.append({"command": raw_command, "status": result["status"], "reason": result["reason"]})
            return result

        # These commands are informational UI operations, not artifact execution.
        if spec.command_id != "artifact.run-demo":
            result = {"status": "RESOLVED", "command_id": spec.command_id,
                      "artifact_id": spec.artifact_id, "artifact_version": spec.artifact_version,
                      "reason": "registered informational action; no code executed"}
            self.ledger.append({"command": spec.command_id, "status": result["status"]})
            return result

        decision = self.gate.evaluate(spec, manifest, artifact_content, confirmed=confirmed)
        result = {"status": decision.status, "command_id": spec.command_id,
                  "artifact_id": decision.artifact_id, "artifact_version": decision.artifact_version,
                  "reason": decision.reason}
        self.ledger.append({"command": spec.command_id, "status": decision.status,
                            "reason": decision.reason, "confirmed": bool(confirmed)})
        return result

    def audit_is_valid(self) -> bool:
        return self.ledger.verify()

    def audit_events(self):
        return self.ledger.events()
