"""Versioned game projects and self-contained HTML exports (no executable imports)."""

import json
from pathlib import Path

GENRES = ("snake", "breakout", "dodge")
MODES = ("standard", "arcade")
MAX_PROJECT_BYTES = 8192
DEFAULT_PROJECT = {
    "version": 1,
    "title": "ELM369 Arcade",
    "genre": "snake",
    "mode": "standard",
    "seed": 369,
    "difficulty": 2,
    "color": "#69e0af",
}


def validate_project(project):
    """Reject unknown fields, executable content, and unbounded runtime settings."""
    if not isinstance(project, dict) or set(project) != set(DEFAULT_PROJECT):
        raise ValueError("Project must contain exactly: " + ", ".join(DEFAULT_PROJECT))
    if type(project["version"]) is not int or project["version"] != 1:
        raise ValueError("Unsupported project version")
    title = project["title"]
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
        raise ValueError("Title must contain 1–80 characters after trimming")
    if any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in title):
        raise ValueError("Title must not contain control characters")
    if project["genre"] not in GENRES or project["mode"] not in MODES:
        raise ValueError("Unsupported genre or mode")
    for name, low, high in (("seed", 0, 4294967295), ("difficulty", 1, 5)):
        if type(project[name]) is not int or not low <= project[name] <= high:
            raise ValueError("{} must be an integer in {}–{}".format(name, low, high))
    color = project["color"]
    if (not isinstance(color, str) or len(color) != 7 or color[0] != "#"
            or any(c not in "0123456789abcdefABCDEF" for c in color[1:])):
        raise ValueError("Color must be #RRGGBB")
    return {**project, "title": title.strip()}


def make_project(**settings):
    return validate_project({**DEFAULT_PROJECT, **settings})


def load_project(path):
    with Path(path).open("rb") as handle:
        content = handle.read(MAX_PROJECT_BYTES + 1)
    if len(content) > MAX_PROJECT_BYTES:
        raise ValueError("Project exceeds 8192 bytes")
    try:
        project = json.loads(content)
    except RecursionError as exc:
        raise ValueError("Project JSON nesting is too deep") from exc
    return validate_project(project)


def render_html(project):
    project = validate_project(project)
    # JSON is data, not code: escape HTML delimiters even inside the inert script.
    payload = (json.dumps(project, ensure_ascii=True)
               .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))
    template = Path(__file__).with_name("studio.html").read_text(encoding="utf-8")
    return template.replace("__ELM_PROJECT_JSON__", payload)
