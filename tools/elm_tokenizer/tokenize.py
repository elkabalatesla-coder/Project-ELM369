"""Tokenizer + prompt-framework scorer (issue #27).

Offline heuristic only — no model downloads, no network.
"""

from __future__ import annotations

import re
from typing import Any

TOKEN = re.compile(r"\w+|[^\w\s]", re.U)

WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"

FRAMEWORKS: dict[str, tuple[str, ...]] = {
    "role": ("you are", "act as", "as a", "your role"),
    "task": ("write", "create", "build", "analyze", "summarize", "extract", "classify"),
    "constraint": ("must", "never", "only", "do not", "don't", "shall not"),
    "format": ("json", "markdown", "bullet", "table", "yaml", "csv"),
    "context": ("given", "context:", "background", "using the following"),
    "evaluation": ("criteria", "rubric", "score", "accept if", "reject if"),
}

WEIGHTS = {
    "role": 0.2,
    "task": 0.25,
    "constraint": 0.2,
    "format": 0.15,
    "context": 0.1,
    "evaluation": 0.1,
}


def frameworks() -> dict[str, Any]:
    return {
        "frameworks": {k: list(v) for k, v in FRAMEWORKS.items()},
        "weights": dict(WEIGHTS),
        "project_id": PROJECT_ID,
        "watermark": WATERMARK,
    }


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text or "")


def score_prompt(text: str) -> dict[str, Any]:
    low = (text or "").lower()
    hits = {k: sum(1 for p in phrases if p in low) for k, phrases in FRAMEWORKS.items()}
    present = [k for k, n in hits.items() if n > 0]
    weighted = round(sum(WEIGHTS[k] for k in present), 3)
    # also expose simple coverage ratio for backwards compatibility
    coverage = round(len(present) / max(len(FRAMEWORKS), 1), 3)
    tokens = tokenize(text)
    if weighted >= 0.75:
        rec = "ALLOW"
    elif weighted >= 0.45:
        rec = "ALLOW_WITH_LIMITS"
    else:
        rec = "MODIFY"
    missing = [k for k in FRAMEWORKS if k not in present]
    return {
        "project_id": PROJECT_ID,
        "token_count": len(tokens),
        "char_count": len(text or ""),
        "tokens_preview": tokens[:40],
        "framework_hits": hits,
        "frameworks_present": present,
        "frameworks_missing": missing,
        "integration_score": weighted,
        "coverage_ratio": coverage,
        "recommendation": rec,
        "watermark": WATERMARK,
    }
