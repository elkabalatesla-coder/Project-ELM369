"""Classify probe results into ok / degraded / down / unknown."""

from __future__ import annotations

import json
from typing import Any

Status = str


def classify_http(status_code: int | None, error: str | None = None) -> Status:
    if error:
        return "down" if _looks_unreachable(error) else "unknown"
    if status_code is None:
        return "unknown"
    if 200 <= status_code < 300:
        return "ok"
    if status_code in {429, 503}:
        return "degraded"
    if status_code >= 500:
        return "down"
    if status_code >= 400:
        return "degraded"
    return "unknown"


def classify_statuspage_v2(payload: Any, http_status: int | None = None) -> Status:
    if not isinstance(payload, dict):
        return classify_http(http_status)
    status = payload.get("status") or {}
    indicator = str(status.get("indicator") or "").lower()
    mapping = {
        "none": "ok",
        "minor": "degraded",
        "major": "down",
        "critical": "down",
        "maintenance": "degraded",
    }
    if indicator in mapping:
        return mapping[indicator]
    return classify_http(http_status)


def parse_json_body(text: str) -> Any | None:
    try:
        return json.loads(text)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _looks_unreachable(error: str) -> bool:
    lowered = error.lower()
    needles = ("timed out", "timeout", "connection", "refused", "unreachable", "name or service")
    return any(n in lowered for n in needles)
