#!/usr/bin/env python3
"""
elm_orchestrator.py

Skeleton orchestrator for Project-ELM369 that reads PROJECT_PYTHON_RUNTIME.json,
validates required fields, and provides simple setup/run hooks.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "PROJECT_PYTHON_RUNTIME.json"

REQUIRED_TOP_LEVEL = ["project", "python", "entrypoint"]


def load_config(path: Path | str = DEFAULT_CONFIG) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_config(cfg: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in cfg]
    if missing:
        raise ValueError(f"PROJECT_PYTHON_RUNTIME.json is missing keys: {missing}")

    py = cfg.get("python", {})
    if "version" not in py:
        raise ValueError("'python.version' is required in PROJECT_PYTHON_RUNTIME.json")


def setup_environment(cfg: Dict[str, Any]) -> None:
    # Placeholder: implement venv creation, dependency install, etc.
    venv = cfg.get("python", {}).get("venv", "venv")
    install_cmd = cfg.get("python", {}).get("install_command", "pip install -r requirements.txt")
    print(f"[orchestrator] Setup: venv={venv}, install='{install_cmd}'")
    # Example: subprocess.run([...]) — left as TODO


def run_entrypoint(cfg: Dict[str, Any]) -> None:
    entrypoint = cfg.get("entrypoint")
    if not entrypoint:
        raise ValueError("No entrypoint defined in config")
    print(f"[orchestrator] Running entrypoint: {entrypoint}")
    # For safety we just print. In a fuller implementation you'd exec/ subprocess the entrypoint.


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="ELM369 Python orchestrator")
    p.add_argument("--config", "-c", default=str(DEFAULT_CONFIG), help="Path to PROJECT_PYTHON_RUNTIME.json")
    p.add_argument("--setup", action="store_true", help="Run setup steps (venv, install)")
    p.add_argument("--run", action="store_true", help="Run configured entrypoint")
    args = p.parse_args(argv)

    cfg = load_config(args.config)
    validate_config(cfg)

    if args.setup:
        setup_environment(cfg)

    if args.run:
        run_entrypoint(cfg)

    if not args.setup and not args.run:
        p.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
