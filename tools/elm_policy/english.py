from __future__ import annotations
from pathlib import Path
from typing import Any

SKIP = {".git", "node_modules", "__pycache__", "artifacts"}


def check_paths(root: Path) -> dict[str, Any]:
    flagged = []
    scanned = 0
    for p in root.rglob("*"):
        if any(part in SKIP for part in p.parts):
            continue
        if not p.is_file() or p.suffix.lower() not in {".md", ".txt"}:
            continue
        scanned += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        # heuristic: high non-ascii ratio excluding common punctuation/emoji in esign docs
        non_ascii = sum(1 for ch in text if ord(ch) > 127)
        if len(text) > 80 and non_ascii / max(len(text), 1) > 0.08:
            flagged.append({"path": str(p), "non_ascii_ratio": round(non_ascii / len(text), 3)})
    return {"scanned": scanned, "flagged": flagged, "ok": len(flagged) == 0, "policy": "US English operator docs preferred"}
