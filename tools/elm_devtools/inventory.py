"""Inventory Project ELM369 tool packages under tools/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY = Path("data/registries/elm369_tools.json")
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"


def _registry_by_path() -> dict[str, dict[str, Any]]:
    if not REGISTRY.is_file():
        return {}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for t in data.get("tools") or []:
        rp = str(t.get("repo_path") or "").rstrip("/")
        if rp:
            out[rp] = t
            # also key by trailing dir name
            out[Path(rp).name] = t
    return out


def list_tools(root: Path | None = None) -> list[dict[str, Any]]:
    base = (root or Path(".")) / "tools"
    reg = _registry_by_path()
    out: list[dict[str, Any]] = []
    if not base.is_dir():
        return out
    for p in sorted(base.iterdir()):
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        readme = p / "README.md"
        tests = p / "tests"
        entry = p / "__main__.py"
        meta = reg.get(f"tools/{p.name}") or reg.get(p.name) or {}
        out.append(
            {
                "id": p.name,
                "path": str(p).replace("\\", "/"),
                "has_readme": readme.is_file(),
                "has_tests": tests.is_dir() and any(tests.glob("test_*.py")),
                "entry": entry.is_file(),
                "registry_id": meta.get("id"),
                "registry_status": meta.get("status"),
                "registry_completion": meta.get("completion"),
            }
        )
    return out


def check_tools(root: Path | None = None) -> dict[str, Any]:
    rows = list_tools(root)
    missing_readme = [r["id"] for r in rows if not r["has_readme"]]
    missing_tests = [r["id"] for r in rows if not r["has_tests"]]
    missing_entry = [r["id"] for r in rows if not r["entry"]]
    unregistered = [r["id"] for r in rows if not r.get("registry_id")]
    return {
        "tool_dirs": len(rows),
        "with_readme": sum(1 for r in rows if r["has_readme"]),
        "with_tests": sum(1 for r in rows if r["has_tests"]),
        "with_entry": sum(1 for r in rows if r["entry"]),
        "missing_readme": missing_readme,
        "missing_tests": missing_tests,
        "missing_entry": missing_entry,
        "unregistered_dirs": unregistered,
        "ok": not missing_tests,  # readme optional for tiny helpers; tests expected
        "watermark": WATERMARK,
    }
