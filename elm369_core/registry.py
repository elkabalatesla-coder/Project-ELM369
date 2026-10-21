"""Append-only in-memory registry with canonical hashes and duplicate protection."""
import hashlib
import json
from typing import Any, Dict, List


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _detached_json_copy(value: Any) -> Any:
    """Detach JSON-compatible values so caller-owned nested objects cannot mutate records."""
    try:
        return json.loads(_canonical_json(value))
    except (TypeError, ValueError) as exc:
        raise ValueError("record_must_be_json_serializable") from exc


class AppendOnlyRegistry:
    """Minimal reference implementation; persistence adapters are intentionally separate."""
    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, Any]] = {}
        self._order: List[str] = []

    def register(self, record_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id_required")
        if not isinstance(record, dict):
            raise ValueError("record_must_be_object")
        if record_id in self._records:
            raise ValueError("immutable_record_id_exists:" + record_id)
        payload = _detached_json_copy(record)
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self._records[record_id] = {"record_id": record_id, "record": payload, "sha256": digest}
        self._order.append(record_id)
        return self.get(record_id)

    def get(self, record_id: str) -> Dict[str, Any]:
        if record_id not in self._records:
            raise KeyError(record_id)
        return _detached_json_copy(self._records[record_id])

    def list_records(self) -> List[Dict[str, Any]]:
        return [self.get(record_id) for record_id in self._order]

    def verify(self, record_id: str) -> bool:
        stored = self.get(record_id)
        expected = hashlib.sha256(_canonical_json(stored["record"]).encode("utf-8")).hexdigest()
        return expected == stored["sha256"]
