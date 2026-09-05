"""Simple tokenizer + prompt-framework scorer (issue #27)."""

from __future__ import annotations

import re
from typing import Any

TOKEN = re.compile(r"\w+|[^\w\s]", re.U)

FRAMEWORKS = {
    "role": ("you are", "act as", "as a"),
    "task": ("write", "create", "build", "analyze", "summarize"),
    "constraint": ("must", "never", "only", "do not", "don't"),
    "format": ("json", "markdown", "bullet", "table"),
}


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text or "")


def score_prompt(text: str) -> dict[str, Any]:
    low = (text or "").lower()
    hits = {k: sum(1 for p in phrases if p in low) for k, phrases in FRAMEWORKS.items()}
    present = [k for k, n in hits.items() if n > 0]
    score = round(len(present) / max(len(FRAMEWORKS), 1), 3)
    tokens = tokenize(text)
    return {
        "token_count": len(tokens),
        "tokens_preview": tokens[:40],
        "framework_hits": hits,
        "frameworks_present": present,
        "integration_score": score,
        "recommendation": "ALLOW" if score >= 0.75 else "ALLOW_WITH_LIMITS" if score >= 0.5 else "MODIFY",
    }
