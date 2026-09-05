from __future__ import annotations
import json
from pathlib import Path
from typing import Any

MANIFEST = Path("artifacts/sandboxes/manifest.json")
GALLERY = Path("artifacts/index.html")


def load() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {"artifacts": [], "error": "missing_manifest"}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    data = load()
    missing = []
    ok = 0
    for a in data.get("artifacts") or []:
        runnable = a.get("runnable")
        if not runnable or not Path(runnable).exists():
            missing.append(a.get("issue"))
        else:
            ok += 1
    return {
        "artifact_count": len(data.get("artifacts") or []),
        "runnable_ok": ok,
        "missing_runnable": missing,
        "gallery_exists": GALLERY.exists(),
        "ok": not missing and GALLERY.exists(),
    }
