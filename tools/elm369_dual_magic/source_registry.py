"""Source metadata storage, not independent source authentication."""

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    uri: str
    authority_level: str
    owner: str
    checked_at_utc: str
    expires_at_utc: Optional[str] = None
    verification_method: str = "manual"
    verified: bool = False
    notes: str = ""


class SourceRegistry:
    """Store caller-declared metadata without fetching or verifying sources."""

    def __init__(self):
        self._sources: Dict[str, SourceRecord] = {}

    def register(self, source: SourceRecord) -> None:
        if not source.source_id.strip():
            raise ValueError("source_id is required")
        if source.source_id in self._sources:
            raise ValueError("duplicate source_id: {}".format(source.source_id))
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> SourceRecord:
        return self._sources[source_id]

    def list_sources(self) -> List[SourceRecord]:
        return sorted(self._sources.values(), key=lambda source: source.source_id)

    def export_json(self) -> str:
        return json.dumps(
            [asdict(source) for source in self.list_sources()],
            indent=2, sort_keys=True, ensure_ascii=False,
        )

    def digest(self) -> str:
        payload = json.dumps(
            [asdict(source) for source in self.list_sources()],
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
