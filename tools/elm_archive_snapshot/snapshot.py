"""Versioned zip snapshot of key ELM369 paths (issues #30/#31/#32)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.elm_orchestrator.esign import watermark
from tools.elm_policy.geofence import stamp_line

DEFAULT_PATHS = [
    "docs",
    "data/registries",
    "openapi",
    "schemas",
    "tools",
    "artifacts/sandboxes/manifest.json",
    "artifacts/index.html",
    "docs/STATUS.md",
    "docs/BACKLOG.md",
]


def make_snapshot(out_dir: Path | None = None, paths: list[str] | None = None) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")
    dest_dir = out_dir or Path("artifacts/snapshots")
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"ELM369_JMR08241978202646902_{stamp}.zip"
    included = []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in paths or DEFAULT_PATHS:
            p = Path(rel)
            if not p.exists():
                continue
            if p.is_file():
                zf.write(p, arcname=str(p))
                included.append(str(p))
            else:
                for f in p.rglob("*"):
                    if f.is_file() and "__pycache__" not in f.parts and ".git" not in f.parts:
                        # skip huge sandbox raw dumps optionally? include all under docs/tools
                        if f.suffix in {".html", ".jsx"} and "sandboxes" in f.parts and f.name != "index.html":
                            continue
                        zf.write(f, arcname=str(f))
                        included.append(str(f))
        meta = watermark(
            {
                "kind": "archive_snapshot",
                "stamp": stamp,
                "location_stamp": stamp_line(),
                "files": len(included),
            }
        )
        zf.writestr("ELM369_SNAPSHOT_META.json", json.dumps(meta, indent=2, ensure_ascii=False))
    return {
        "zip": str(zip_path),
        "files": len(included),
        "stamp": stamp,
        "location_stamp": stamp_line(),
        "meta": meta,
    }
