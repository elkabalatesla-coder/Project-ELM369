"""One-shot Project ELM369 health report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build() -> dict[str, Any]:
    sections: dict[str, Any] = {}
    errors: list[str] = []

    try:
        from tools.elm_orchestrator.agents import diagnose
        sections["diag"] = diagnose()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"diag:{exc}")
        sections["diag"] = {"ok": False, "error": str(exc)}

    try:
        from tools.elm_progress.engine import summarize, verify_paths
        sections["progress"] = summarize()
        sections["paths"] = verify_paths()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"progress:{exc}")

    try:
        from tools.grok_archive.status import vault_status
        sections["vault"] = vault_status()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"vault:{exc}")

    try:
        from tools.elm_artifacts.catalog import verify as artifacts_verify
        sections["artifacts"] = artifacts_verify()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"artifacts:{exc}")

    try:
        from tools.elm_devtools.inventory import list_tools
        tools = list_tools()
        sections["devtools"] = {
            "tool_dirs": len(tools),
            "with_tests": sum(1 for t in tools if t.get("has_tests")),
            "with_readme": sum(1 for t in tools if t.get("has_readme")),
        }
    except Exception as exc:  # noqa: BLE001
        errors.append(f"devtools:{exc}")

    ok = (
        bool(sections.get("diag", {}).get("ok"))
        and bool(sections.get("artifacts", {}).get("ok", True))
        and not errors
    )
    return {
        "project_id": "ELM369_JMR08241978202646902",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "errors": errors,
        "sections": sections,
    }
