"""Offline phrase glossary (issue #25 / AUDIO-TX).

DONE as an offline operator/ELM phrase tool.
Not a full audio translator — no STT/TTS, no live MT API, no SMS/phone.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

GLOSSARY = Path("tools/elm_translator/data/glossary.json")
WATERMARK = "Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902"
PROJECT_ID = "ELM369_JMR08241978202646902"
TOOL_ID = "AUDIO-TX"
TOOL_STATUS = "DONE"


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


def _english_phrases(data: dict[str, Any] | None = None) -> list[str]:
    data = data or load()
    return [str(e.get("en", "")).strip() for e in (data.get("entries") or []) if e.get("en")]


def suggest(text: str, *, n: int = 3, cutoff: float = 0.5) -> list[str]:
    """Nearest English glossary phrases via stdlib difflib (exact-miss helper)."""
    phrases = _english_phrases()
    key = text.strip().lower()
    if not key or not phrases:
        return []
    by_lower = {p.lower(): p for p in phrases}
    matches = difflib.get_close_matches(key, list(by_lower.keys()), n=n, cutoff=cutoff)
    return [by_lower[m] for m in matches]


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
            "suggestions": [],
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
        "suggestions": suggest(text),
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


def search(query: str, *, limit: int = 20) -> dict[str, Any]:
    """Substring search across en/es/fr/de fields (case-insensitive)."""
    data = load()
    q = (query or "").strip().lower()
    hits: list[dict[str, Any]] = []
    if not q:
        return {
            "ok": False,
            "error": "empty_query",
            "query": query,
            "matches": [],
            "count": 0,
            "audio": False,
            "watermark": WATERMARK,
        }
    for e in data.get("entries") or []:
        blob = " ".join(str(e.get(k, "")) for k in ("en", "es", "fr", "de")).lower()
        if q in blob:
            hits.append(e)
            if len(hits) >= limit:
                break
    return {
        "ok": True,
        "query": query,
        "matches": hits,
        "count": len(hits),
        "audio": False,
        "project_id": data.get("project_id") or PROJECT_ID,
        "watermark": WATERMARK,
    }


def coverage() -> dict[str, Any]:
    """Per-language glossary coverage / completeness."""
    data = load()
    entries = list(data.get("entries") or [])
    langs = [L for L in languages() if L != "en"] or ["es", "fr", "de"]
    total = len(entries)
    per_lang: dict[str, Any] = {}
    for lang in langs:
        filled = sum(1 for e in entries if e.get(lang))
        per_lang[lang] = {
            "filled": filled,
            "missing": total - filled,
            "pct": round((100.0 * filled / total), 1) if total else 0.0,
        }
    return {
        "ok": True,
        "tool_id": TOOL_ID,
        "entry_count": total,
        "languages": languages(),
        "per_language": per_lang,
        "complete": all(v["missing"] == 0 for v in per_lang.values()) if per_lang else False,
        "audio": False,
        "project_id": data.get("project_id") or PROJECT_ID,
        "watermark": WATERMARK,
    }


def status() -> dict[str, Any]:
    """AUDIO-TX status: DONE as offline phrase tool; document hard non-goals."""
    cov = coverage()
    return {
        "ok": True,
        "tool_id": TOOL_ID,
        "name": "Audio Translator (offline phrase glossary)",
        "status": TOOL_STATUS,
        "scope": "offline_phrase_glossary",
        "entry_count": cov["entry_count"],
        "languages": cov["languages"],
        "coverage": cov["per_language"],
        "commands": ["translate", "batch", "list", "langs", "search", "coverage", "status"],
        "non_goals": [
            "No STT / speech-to-text",
            "No TTS / text-to-speech",
            "No audio capture or playback pipeline",
            "No live neural machine-translation API",
            "No SMS / phone / telephony actuation",
        ],
        "audio": False,
        "project_id": PROJECT_ID,
        "watermark": WATERMARK,
    }
