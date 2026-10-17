"""Load and render the project's AI and writing skill guidance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

REGISTRY = Path(__file__).with_name("skillsets.json")


def load_skillsets() -> list[dict[str, Any]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return list(data.get("skillsets") or [])


def get_skillsets(category: str | None = None) -> list[dict[str, Any]]:
    skills = load_skillsets()
    if category is None:
        return skills
    normalized = category.strip().casefold()
    return [skill for skill in skills if skill.get("category", "").casefold() == normalized]


def get_skillset(skill_id: str) -> dict[str, Any]:
    normalized = skill_id.strip().casefold()
    for skill in load_skillsets():
        if skill.get("id", "").casefold() == normalized:
            return skill
    raise KeyError(f"unknown skillset: {skill_id}")


def render_guidance(skill_ids: Iterable[str]) -> str:
    sections = []
    for skill_id in skill_ids:
        skill = get_skillset(skill_id)
        checklist = "\n".join(f"- {item}" for item in skill.get("guidance", []))
        sections.append(f"## {skill['name']}\n{checklist}")
    return "\n\n".join(sections)
