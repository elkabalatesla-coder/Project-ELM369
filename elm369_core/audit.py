"""Hash-linked audit event records for deterministic verification."""
import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional

GENESIS_HASH = "0" * 64


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_chain(events: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a hash-linked copy of events; each event needs an event_id and type."""
    result: List[Dict[str, Any]] = []
    previous = GENESIS_HASH
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("event_must_be_object")
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event_id_required")
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type_required")
        if event_id in seen:
            raise ValueError("duplicate_event_id:" + event_id)
        seen.add(event_id)
        payload = dict(event)
        payload["previous_hash"] = previous
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        record = dict(payload)
        record["event_hash"] = digest
        result.append(record)
        previous = digest
    return result


def verify_chain(records: Iterable[Dict[str, Any]]) -> bool:
    previous = GENESIS_HASH
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            return False
        digest = record.get("event_hash")
        payload = dict(record)
        payload.pop("event_hash", None)
        if payload.get("previous_hash") != previous:
            return False
        event_id = payload.get("event_id")
        if not isinstance(event_id, str) or event_id in seen:
            return False
        seen.add(event_id)
        expected = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        if digest != expected:
            return False
        previous = digest
    return True
