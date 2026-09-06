"""Offline phrase glossary (issue #25).

Not a full audio translator — no STT/TTS, no live MT API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GLOSSARY = Path("tools/elm_translator/data/glossary.json")
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"


def load() -> dict[str, Any]:
    return json.loads(GLOSSARY.read_text(encoding="utf-8"))


def languages() -> list[str]:
    data = load()
    langs = list(data.get("languages") or [])
    if not langs:
        langs = ["en"]
        for e in data.get("entries") or []:
            for k in e:
                if k not in langs:
                    langs.append(k)
    return langs


def translate(text: str, *, to: str = "es") -> dict[str, Any]:
    data = load()
    key = text.strip().lower()
    to = (to or "es").lower()
    known = languages()
    if to not in known and to != "en":
        return {
            "ok": False,
            "error": "unsupported_language",
            "input": text,
            "target": to,
            "supported": known,
            "hint": "Extend tools/elm_translator/data/glossary.json languages/entries",
            "audio": False,
            "watermark": WATERMARK,
        }
    for e in data.get("entries") or []:
        if str(e.get("en", "")).lower() == key:
            out = e.get(to)
            return {
                "ok": out is not None,
                "source": "en",
                "target": to,
                "input": text,
                "output": out,
                "entry": e,
                "audio": False,
                "note": "Phrase glossary only — no audio pipeline.",
                "project_id": data.get("project_id") or PROJECT_ID,
                "watermark": WATERMARK,
            }
    return {
        "ok": False,
        "error": "not_in_glossary",
        "input": text,
        "target": to,
        "hint": "Extend tools/elm_translator/data/glossary.json",
        "audio": False,
        "watermark": WATERMARK,
    }


def translate_many(texts: list[str], *, to: str = "es") -> dict[str, Any]:
    rows = [translate(t, to=to) for t in texts]
    return {
        "ok": all(r.get("ok") for r in rows) if rows else False,
        "count": len(rows),
        "results": rows,
        "audio": False,
        "watermark": WATERMARK,
    }
