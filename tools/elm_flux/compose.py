"""FLUX / image-prompt composer (issue #28).

Dry-run by default — never calls external image APIs.
Live FLUX / Wavespeed / HF generation is an intentional non-goal for this tool
until Joseph explicitly opts in later.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DEFAULT_MODEL = "black-forest-labs/FLUX.1-dev"
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"

STYLES: dict[str, str] = {
    "cyberpunk": "cyberpunk aesthetic, neon lights, high detail, cinematic lighting",
    "noir": "film noir, high contrast, moody shadows, grain",
    "watercolor": "watercolor painting, soft washes, paper texture",
    "photoreal": "photorealistic, natural lighting, sharp focus, 85mm lens",
    "liquid3d": "liquid 3D form, translucent volume, refractive highlights",
    "schematic": "technical schematic, clean lines, annotated diagram",
}

ASPECTS = ("1:1", "16:9", "9:16", "4:3", "3:4", "21:9")


def list_styles() -> dict[str, Any]:
    return {
        "styles": sorted(STYLES),
        "aspects": list(ASPECTS),
        "default_model": DEFAULT_MODEL,
        "generate": False,
        "note": "Dry-run composer only — no live FLUX API.",
    }


def compose(
    prompt: str,
    *,
    style: str = "cyberpunk",
    model: str = DEFAULT_MODEL,
    aspect: str = "1:1",
    negative: str = "",
) -> dict[str, Any]:
    prompt = (prompt or "").strip()
    style_key = (style or "cyberpunk").lower()
    style_tail = STYLES.get(style_key, f"{style_key} aesthetic, high detail, cinematic lighting")
    aspect = aspect if aspect in ASPECTS else "1:1"
    neg = (negative or "").strip() or "blurry, low quality, watermark text, deformed hands"
    enriched = f"{prompt}, {style_tail}".strip(", ")
    return {
        "project_id": PROJECT_ID,
        "model": model,
        "prompt": prompt,
        "enriched_prompt": enriched,
        "negative_prompt": neg,
        "style": style_key,
        "aspect": aspect,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "generate": False,
        "live_api": False,
        "note": "Dry-run composer only. CI and default CLI never call out. Live FLUX API is not wired.",
        "watermark": WATERMARK,
    }


def generate_stub(composed: dict[str, Any], *, token_present: bool) -> dict[str, Any]:
    """Refuse real generation — document requirements only."""
    base = {**composed, "generate": False, "live_api": False}
    if not token_present:
        return {
            **base,
            "ok": False,
            "error": "missing_token",
            "hint": "Set WAVESPEED_API_TOKEN or HF_TOKEN only if a future opt-in generator is approved. Scaffold still will not call out.",
        }
    return {
        **base,
        "ok": False,
        "error": "generator_not_wired",
        "hint": "Scaffold intentionally does not call external image APIs. Keep dry-run.",
    }
