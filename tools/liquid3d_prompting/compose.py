"""Compose Liquid-3D prompt packets from templates."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"
MODES = {"visual", "audio", "animation", "combo"}


@dataclass
class PromptPacket:
    prompt_id: str
    project_id: str
    mode: str
    subject: str
    rendered: str
    created_at: str
    palette: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


def load_config(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or DEFAULT_CONFIG).read_text(encoding="utf-8"))


def compose(
    subject: str,
    *,
    mode: str = "visual",
    tags: Iterable[str] | None = None,
    palette: Iterable[str] | None = None,
    constraints: Iterable[str] | None = None,
    config: dict[str, Any] | None = None,
) -> PromptPacket:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {sorted(MODES)}")
    if not subject.strip():
        raise ValueError("subject must be non-empty")

    cfg = config or load_config()
    template = (cfg.get("templates") or {}).get(mode)
    if not template:
        raise KeyError(f"missing template for mode={mode}")

    colors = list(palette) if palette is not None else list(cfg.get("default_palette") or [])
    constr = (
        list(constraints)
        if constraints is not None
        else list(cfg.get("default_constraints") or [])
    )
    palette_text = ", ".join(colors) if colors else "cyan/magenta liquid defaults"
    constr_text = "; ".join(constr) if constr else "none"

    rendered = template.format(
        subject=subject.strip(),
        palette=palette_text,
        constraints=constr_text,
    )
    return PromptPacket(
        prompt_id=str(uuid.uuid4()),
        project_id=str(cfg.get("project_id", "")),
        mode=mode,
        subject=subject.strip(),
        rendered=rendered,
        created_at=datetime.now(timezone.utc).isoformat(),
        palette=colors,
        tags=[t.strip() for t in (tags or []) if t and t.strip()],
        constraints=constr,
    )


def packet_to_json(packet: PromptPacket) -> str:
    return json.dumps(asdict(packet), ensure_ascii=False, indent=2)


def list_templates(config: dict[str, Any] | None = None) -> dict[str, str]:
    cfg = config or load_config()
    return dict(cfg.get("templates") or {})
