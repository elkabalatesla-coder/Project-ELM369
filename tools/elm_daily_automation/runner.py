"""Run configured daily automation tasks and persist a JSONL log."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tools.elm_daily_automation.vault_backlog import backlog_report

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"
DEFAULT_LOG = ROOT / "data" / "daily_runs.jsonl"

OutageRunner = Callable[[], dict[str, Any]]


@dataclass
class TaskResult:
    task_id: str
    name: str
    status: str
    detail: str
    items: list[str] = field(default_factory=list)


@dataclass
class RunReport:
    project_id: str
    started_at: str
    finished_at: str
    dry_run: bool
    results: list[TaskResult]

    @property
    def ok(self) -> bool:
        return all(r.status in {"ok", "skipped", "noted"} for r in self.results)


def load_config(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or DEFAULT_CONFIG).read_text(encoding="utf-8"))


def default_outage_runner(*, dry_run: bool) -> dict[str, Any]:
    from tools.ai_outage_monitor.check import run_checks

    probes = run_checks(dry_run=dry_run)
    bad = [p for p in probes if p.status in {"down", "degraded", "unknown"}]
    return {
        "status": "ok" if not bad else "attention",
        "detail": f"{len(probes)} probed, {len(bad)} need attention",
        "services": [{"id": p.service_id, "status": p.status} for p in probes],
    }


def run_daily(
    config: dict[str, Any] | None = None,
    *,
    dry_run: bool = False,
    outage_runner: OutageRunner | None = None,
    log_path: Path | None = None,
) -> RunReport:
    cfg = config or load_config()
    started = datetime.now(timezone.utc).isoformat()
    results: list[TaskResult] = []

    for task in cfg.get("tasks", []):
        if not task.get("enabled", True):
            results.append(
                TaskResult(task["id"], task["name"], "skipped", "disabled in config")
            )
            continue

        kind = task.get("kind")
        if kind == "outage_monitor":
            runner = outage_runner or (lambda: default_outage_runner(dry_run=dry_run))
            payload = runner()
            results.append(
                TaskResult(
                    task["id"],
                    task["name"],
                    payload.get("status", "unknown"),
                    payload.get("detail", ""),
                )
            )
        elif kind == "checklist":
            items = list(task.get("items") or [])
            results.append(
                TaskResult(
                    task["id"],
                    task["name"],
                    "noted",
                    f"{len(items)} reminders",
                    items=items,
                )
            )
        elif kind == "vault_backlog":
            root = Path(task["sources_root"]) if task.get("sources_root") else None
            payload = backlog_report(root)
            results.append(
                TaskResult(
                    task["id"],
                    task["name"],
                    payload.get("status", "noted"),
                    payload.get("detail", ""),
                    items=[
                        f"{src}: {counts.get('open', 0)} open / {counts.get('total', 0)} total"
                        for src, counts in (payload.get("by_source") or {}).items()
                    ],
                )
            )
        else:
            results.append(
                TaskResult(task["id"], task["name"], "unknown", f"unsupported kind: {kind}")
            )

    finished = datetime.now(timezone.utc).isoformat()
    report = RunReport(
        project_id=str(cfg.get("project_id", "")),
        started_at=started,
        finished_at=finished,
        dry_run=dry_run,
        results=results,
    )
    _append_log(report, log_path or DEFAULT_LOG)
    return report


def _append_log(report: RunReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project_id": report.project_id,
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "dry_run": report.dry_run,
        "ok": report.ok,
        "results": [asdict(r) for r in report.results],
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
