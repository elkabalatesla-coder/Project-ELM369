"""Strict, allowlist-based command registry for the ELM369 keyboard prototype.

This module resolves command IDs; it deliberately never evaluates user-supplied code.
Python 3.8+ compatible, standard library only.
"""
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple
import re

_COMMAND_RE = re.compile(r"^/[a-z][a-z0-9-]{0,47}$")
_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{2,127}$")


@dataclass(frozen=True)
class CommandSpec:
    command_id: str
    artifact_id: str
    artifact_version: str
    label: str
    capabilities: Tuple[str, ...] = ()
    risk_class: str = "low"
    requires_confirmation: bool = False
    enabled: bool = True

    def __post_init__(self) -> None:
        if not _ID_RE.fullmatch(self.command_id):
            raise ValueError("invalid command_id")
        if not _ID_RE.fullmatch(self.artifact_id):
            raise ValueError("invalid artifact_id")
        if not self.artifact_version or any(c.isspace() for c in self.artifact_version):
            raise ValueError("artifact_version must be a non-empty token")
        if self.risk_class not in {"low", "medium", "high", "critical"}:
            raise ValueError("unsupported risk_class")
        if any(not _ID_RE.fullmatch(cap) for cap in self.capabilities):
            raise ValueError("invalid capability")


class CommandRegistry:
    """Immutable-by-interface registry with explicit slash-command aliases."""
    def __init__(self, specs: Iterable[CommandSpec], aliases: Mapping[str, str]):
        spec_map: Dict[str, CommandSpec] = {}
        for spec in specs:
            if spec.command_id in spec_map:
                raise ValueError("duplicate command_id")
            spec_map[spec.command_id] = spec
        alias_map: Dict[str, str] = {}
        for alias, command_id in aliases.items():
            if not _COMMAND_RE.fullmatch(alias):
                raise ValueError("invalid alias: %s" % alias)
            if command_id not in spec_map:
                raise ValueError("alias points to unknown command_id")
            if alias in alias_map:
                raise ValueError("duplicate alias")
            alias_map[alias] = command_id
        self._specs = spec_map
        self._aliases = alias_map

    def resolve(self, raw_command: str) -> Optional[CommandSpec]:
        """Resolve the first whitespace-delimited token only; reject malformed input."""
        if not isinstance(raw_command, str):
            return None
        parts = raw_command.strip().split()
        if not parts or not _COMMAND_RE.fullmatch(parts[0]):
            return None
        command_id = self._aliases.get(parts[0])
        if command_id is None:
            return None
        spec = self._specs[command_id]
        return spec if spec.enabled else None

    def list_enabled(self) -> Tuple[CommandSpec, ...]:
        return tuple(sorted((s for s in self._specs.values() if s.enabled), key=lambda s: s.command_id))


def default_registry() -> CommandRegistry:
    specs = (
        CommandSpec("artifact.library", "elm369.artifact-library.demo", "0.1.0", "List demo artifacts"),
        CommandSpec("artifact.validate", "elm369.artifact-validation.demo", "0.1.0", "Validate demo manifest", ("registry.read",)),
        CommandSpec("artifact.run-demo", "elm369.keyboard.safe-demo", "0.1.0", "Run simulated demo", ("sandbox.execute",), "low", True),
        CommandSpec("audit.history", "elm369.audit-history.demo", "0.1.0", "Show session history", ("audit.read",)),
        CommandSpec("device.profile", "elm369.device-profile.demo", "0.1.0", "Select device profile"),
        CommandSpec("help.show", "elm369.keyboard-help.demo", "0.1.0", "Show command help"),
    )
    aliases = {
        "/library": "artifact.library",
        "/validate": "artifact.validate",
        "/run": "artifact.run-demo",
        "/history": "audit.history",
        "/settings": "device.profile",
        "/help": "help.show",
    }
    return CommandRegistry(specs, aliases)
