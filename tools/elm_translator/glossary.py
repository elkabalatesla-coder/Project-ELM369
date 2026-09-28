"""Offline phrase glossary (issue #25).

Not a full audio translator — no STT/TTS, no live MT API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MODULE_ROOT = Path(__file__).resolve().parent
GLOSSARY = MODULE_ROOT / "data" / "glossary.json"
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


def _read_text_items(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8")
    if suffix == ".json":
        data = json.loads(raw)
        if not isinstance(data, list) or any(not isinstance(item, str) for item in data):
            raise ValueError("json_input_must_be_a_list_of_strings")
        return [item for item in data if item.strip()]
    return [line.strip() for line in raw.splitlines() if line.strip()]


def translate_file(path: str | Path, *, to: str = "es") -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {
            "ok": False,
            "error": "input_file_not_found",
            "input_path": str(source),
            "target": (to or "es").lower(),
            "audio": False,
            "watermark": WATERMARK,
        }
    try:
        texts = _read_text_items(source)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "invalid_json_input",
            "input_path": str(source),
            "target": (to or "es").lower(),
            "audio": False,
            "watermark": WATERMARK,
        }
    except ValueError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "input_path": str(source),
            "target": (to or "es").lower(),
            "audio": False,
            "watermark": WATERMARK,
        }

    translated = translate_many(texts, to=to)
    translated.update(
        {
            "mode": "file_pipeline",
            "input_path": str(source),
            "input_format": "json" if source.suffix.lower() == ".json" else "text",
        }
    )
    return translated
