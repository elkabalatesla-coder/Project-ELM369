from __future__ import annotations
from typing import Any

HOME = {
    "city": "Kokomo",
    "region": "Indiana",
    "postal_code": "46902",
    "country": "USA",
    "operator": "Joseph Michael Rose",
    "project_id": "ELM369_JMR08241978202646902",
    "session_uuid": "1550e4d5-9ee3-49cd-8af8-7c9d630f84ad",
    "esign": {"name": "Joseph Michael Rose", "initials": "IX JR", "symbol": "🌹"},
}


def location() -> dict[str, Any]:
    return dict(HOME)


def stamp_line() -> str:
    return f"{HOME['city']}, {HOME['region']} {HOME['postal_code']} USA · {HOME['operator']} · {HOME['esign']['initials']} {HOME['esign']['symbol']}"
