"""Case queue summary helpers (Ziggy CASE-YYYYMMDD-NNN pattern)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

CASE_RE = re.compile(r"CASE-(\d{8})-(\d{3})\b")


def summarize_case_queue(root: Path | None = None) -> dict[str, Any]:
    """Scan vault + data for CASE-* ids; summary only (no mutation)."""
    base = root or Path(".")
    found: dict[str, dict[str, Any]] = {}
    scan_roots = [
        base / "vault",
        base / "data",
        base / "docs",
    ]
    for scan in scan_roots:
        if not scan.exists():
            continue
        for path in scan.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".json", ".jsonl", ".txt", ".yml", ".yaml"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in CASE_RE.finditer(text):
                cid = m.group(0)
                found.setdefault(
                    cid,
                    {"id": cid, "date": m.group(1), "seq": m.group(2), "paths": []},
                )
                rel = str(path)
                if rel not in found[cid]["paths"]:
                    found[cid]["paths"].append(rel)

    cases = sorted(found.values(), key=lambda c: (c["date"], c["seq"]), reverse=True)
    return {
        "pattern": "CASE-YYYYMMDD-NNN",
        "collector": "Ziggy",
        "open_count": len(cases),
        "cases": cases[:50],
        "note": "Summary scan only — filing remains Joseph-gated.",
    }
