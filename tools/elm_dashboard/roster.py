"""Live Grok bot roster lanes for the AI hub board."""

from __future__ import annotations

from typing import Any

# Mirror of docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md
ROSTER: list[dict[str, Any]] = [
    {
        "lane": "intake",
        "bot": "Ziggy",
        "role": "complaint/case collector",
        "id_pattern": "CASE-YYYYMMDD-NNN",
        "status": "OPERATIONAL",
    },
    {
        "lane": "vault",
        "bot": "Hope",
        "role": "vault/ELM tips",
        "status": "OPERATIONAL",
    },
    {
        "lane": "media",
        "bot": "Vid Cambot",
        "role": "media capture/assist",
        "status": "OPERATIONAL",
    },
    {
        "lane": "research",
        "bot": "Private Eye X",
        "role": "9:30 dig",
        "status": "OPERATIONAL",
    },
    {
        "lane": "defense",
        "bot": "Red Dragon Samurai Knight",
        "role": "offense-for-defense",
        "authorization": "Joseph / Ziggy authorize",
        "status": "OPERATIONAL",
    },
    {
        "lane": "guardian",
        "bot": "Orange Ninja",
        "role": "silent guardian",
        "status": "OPERATIONAL",
    },
    {
        "lane": "threat",
        "bot": "White Rook",
        "role": "malware/threat/scam guard",
        "status": "OPERATIONAL",
    },
    {
        "lane": "reserve",
        "bot": "New Bot",
        "role": "placeholder TBD",
        "status": "PLACEHOLDER",
    },
]


def roster_lanes() -> list[dict[str, Any]]:
    return [dict(r) for r in ROSTER]
