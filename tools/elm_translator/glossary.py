from __future__ import annotations
import json
from pathlib import Path
from typing import Any

GLOSSARY = Path("tools/elm_translator/data/glossary.json")

def load() -> dict[str, Any]:
    return json.loads(GLOSSARY.read_text(encoding="utf-8"))

def translate(text: str, *, to: str = "es") -> dict[str, Any]:
    data = load()
    key = text.strip().lower()
    for e in data.get("entries") or []:
        if str(e.get("en","")).lower() == key:
            return {"ok": True, "source": "en", "target": to, "input": text, "output": e.get(to), "entry": e}
    return {"ok": False, "error": "not_in_glossary", "input": text, "hint": "Extend tools/elm_translator/data/glossary.json"}
