from __future__ import annotations
import ast
from pathlib import Path
from typing import Any

def list_tools(root: Path | None = None) -> list[dict[str, Any]]:
    base = (root or Path(".")) / "tools"
    out = []
    if not base.is_dir():
        return out
    for p in sorted(base.iterdir()):
        if not p.is_dir() or p.name.startswith(("_",".")):
            continue
        readme = p / "README.md"
        out.append({
            "id": p.name,
            "path": str(p),
            "has_readme": readme.is_file(),
            "has_tests": (p / "tests").is_dir(),
            "entry": (p / "__main__.py").is_file(),
        })
    return out
