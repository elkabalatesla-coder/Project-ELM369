from __future__ import annotations

from typing import Any

from tools.elm_policy.geofence import HOME, stamp_line

PRIMARY_ID = "JMR08241978202646902"
COMPANION_ID = "JMR0824197846902"
SPINE_ID = "operator-spine-v0.1"


def envelope(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Attach dual-ID + Kokomo e-sign provenance to a Spine response."""
    out: dict[str, Any] = {
        "spine": SPINE_ID,
        "dual_id": {
            "primary": PRIMARY_ID,
            "companion": COMPANION_ID,
            "session_uuid": HOME.get("session_uuid"),
        },
        "location": {
            "city": HOME["city"],
            "region": HOME["region"],
            "postal_code": HOME["postal_code"],
            "country": HOME["country"],
        },
        "esign": dict(HOME["esign"]),
        "operator": HOME["operator"],
        "stamp": stamp_line(),
    }
    if payload is not None:
        out["data"] = payload
    return out
