"""FLUX / image-prompt composer (issue #28). Dry-run by default — no network."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DEFAULT_MODEL = "black-forest-labs/FLUX.1-dev"


def compose(prompt: str, *, style: str = "cyberpunk", model: str = DEFAULT_MODEL) -> dict[str, Any]:
    prompt = (prompt or "").strip()
    enriched = f"{prompt}, {style} aesthetic, high detail, cinematic lighting".strip(", ")
    return {
        "model": model,
        "prompt": prompt,
        "enriched_prompt": enriched,
        "style": style,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "generate": False,
        "note": "Dry-run composer only. Pass --generate only with your own API token via env; CI never calls out.",
    }


def generate_stub(composed: dict[str, Any], *, token_present: bool) -> dict[str, Any]:
    """Refuse real generation in scaffold; document requirements."""
    if not token_present:
        return {**composed, "ok": False, "error": "missing_token", "hint": "Set WAVESPEED_API_TOKEN or HF_TOKEN to enable a future generator."}
    return {
        **composed,
        "ok": False,
        "error": "generator_not_wired",
        "hint": "Scaffold intentionally does not call external image APIs yet.",
    }
