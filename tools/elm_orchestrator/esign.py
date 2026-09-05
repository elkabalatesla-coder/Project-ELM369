"""Local provenance watermark / e-sign metadata scaffold (not a PKI CA)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from tools.elm_orchestrator.agents import PROJECT_ID


def watermark(payload: dict[str, Any], *, initials: str = "IX JR", symbol: str = "🌹") -> dict[str, Any]:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "project_id": PROJECT_ID,
        "signatory": "Joseph Michael Rose",
        "initials": initials,
        "e_symbol": symbol,
        "auto_esign": True,
        "auto_watermark": True,
        "payload_sha256": digest,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "disclaimer": "Local provenance watermark only — not a certificate-authority signature.",
    }
