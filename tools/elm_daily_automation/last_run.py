"""Read-only helper: summarize the latest ELM daily automation Actions run."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

DEFAULT_REPO = "elkabalatesla-coder/Project-ELM369"
DEFAULT_WORKFLOW = "elm-daily-automation-schedule.yml"
DEFAULT_ARTIFACT = "elm-daily-run-log"
DEFAULT_LOCAL_LOG = Path(__file__).resolve().parent / "data" / "daily_runs.jsonl"
ON_BOX_PAT = Path("/home/box/.config/gh/pat")

EXIT_OK = 0
EXIT_ATTENTION = 1
EXIT_IN_PROGRESS = 2
EXIT_AUTH = 3
EXIT_NO_RUNS = 4

GhRunner = Callable[[Sequence[str], dict[str, str] | None], subprocess.CompletedProcess[str]]


@dataclass
class LastRunReport:
    source: str
    repo: str
    status: str
    conclusion: str | None
    started_at: str | None
    updated_at: str | None
    url: str | None
    display_title: str | None = None
    run_id: int | str | None = None
    attention: list[str] = field(default_factory=list)
    auth_unavailable: bool = False
    detail: str = ""

    def exit_code(self) -> int:
        if self.auth_unavailable:
            return EXIT_AUTH
        if self.source == "none" or self.status == "none":
            return EXIT_NO_RUNS
        status = (self.status or "").lower()
        if status in {"in_progress", "queued", "pending", "waiting", "requested"}:
            return EXIT_IN_PROGRESS
        conclusion = (self.conclusion or "").lower()
        if status == "completed" and conclusion == "success" and not self.attention:
            return EXIT_OK
        if status == "completed" and conclusion in {"failure", "cancelled", "timed_out"}:
            return EXIT_ATTENTION
        if self.attention:
            return EXIT_ATTENTION
        if status == "completed" and conclusion == "success":
            return EXIT_OK
        return EXIT_ATTENTION


def _env_with_token(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    if env.get("GH_TOKEN") or env.get("GITHUB_TOKEN") or env.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
        return env
    if ON_BOX_PAT.is_file():
        token = ON_BOX_PAT.read_text(encoding="utf-8").strip()
        if token:
            env["GH_TOKEN"] = token
    return env


def default_gh_runner(args: Sequence[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        env=_env_with_token(env),
        check=False,
    )


def _is_auth_failure(proc: subprocess.CompletedProcess[str]) -> bool:
    blob = f"{proc.stderr or ''}\n{proc.stdout or ''}".lower()
    needles = (
        "auth_unavailable",
        "not logged into any github hosts",
        "authentication required",
        "bad credentials",
        "http 401",
        "401 unauthorized",
        "to get started with github cli",
        "gh auth login",
        "no github token",
    )
    return any(n in blob for n in needles) or proc.returncode in {4, 127} and "gh" in blob


def _attention_from_log_payload(payload: dict[str, Any]) -> list[str]:
    attention: list[str] = []
    if payload.get("ok") is False:
        attention.append("run_ok=false")
    for result in payload.get("results") or []:
        status = str(result.get("status") or "").lower()
        task_id = str(result.get("task_id") or result.get("name") or "task")
        detail = str(result.get("detail") or "")
        if status in {"attention", "failure", "failed", "error", "down", "degraded"}:
            attention.append(f"{task_id}:{status}:{detail}"[:160])
        elif status == "noted" and "skipped/unavailable" in detail.lower():
            attention.append(f"{task_id}:noted:{detail}"[:160])
    return attention


def _parse_local_log(path: Path) -> LastRunReport | None:
    if not path.is_file():
        return None
    last: dict[str, Any] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last = json.loads(line)
        except json.JSONDecodeError:
            continue
    if not last:
        return None
    attention = _attention_from_log_payload(last)
    ok = bool(last.get("ok", True)) and not attention
    return LastRunReport(
        source="local",
        repo=DEFAULT_REPO,
        status="completed",
        conclusion="success" if ok else "attention",
        started_at=last.get("started_at"),
        updated_at=last.get("finished_at"),
        url=None,
        attention=attention,
        detail="from local daily_runs.jsonl",
    )


def _list_latest_run(
    *,
    repo: str,
    workflow: str,
    gh: GhRunner,
) -> tuple[dict[str, Any] | None, LastRunReport | None]:
    proc = gh(
        [
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            workflow,
            "--limit",
            "1",
            "--json",
            "databaseId,status,conclusion,createdAt,updatedAt,url,displayTitle,event",
        ],
        None,
    )
    if proc.returncode != 0:
        if _is_auth_failure(proc):
            return None, LastRunReport(
                source="actions",
                repo=repo,
                status="auth_unavailable",
                conclusion=None,
                started_at=None,
                updated_at=None,
                url=None,
                auth_unavailable=True,
                detail="auth_unavailable",
            )
        return None, LastRunReport(
            source="actions",
            repo=repo,
            status="error",
            conclusion=None,
            started_at=None,
            updated_at=None,
            url=None,
            detail=(proc.stderr or proc.stdout or "gh run list failed").strip()[:240],
            attention=["gh_run_list_failed"],
        )
    try:
        runs = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return None, LastRunReport(
            source="actions",
            repo=repo,
            status="error",
            conclusion=None,
            started_at=None,
            updated_at=None,
            url=None,
            detail="invalid json from gh run list",
            attention=["invalid_gh_json"],
        )
    if not runs:
        return None, LastRunReport(
            source="none",
            repo=repo,
            status="none",
            conclusion=None,
            started_at=None,
            updated_at=None,
            url=None,
            detail="no runs found",
        )
    return runs[0], None


def _download_attention(
    *,
    repo: str,
    run_id: int | str,
    artifact: str,
    gh: GhRunner,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="elm-daily-last-run-") as tmp:
        proc = gh(
            [
                "run",
                "download",
                str(run_id),
                "--repo",
                repo,
                "-n",
                artifact,
                "-D",
                tmp,
            ],
            None,
        )
        if proc.returncode != 0:
            return []
        log_path = None
        for path in Path(tmp).rglob("*.jsonl"):
            log_path = path
            break
        if log_path is None:
            for path in Path(tmp).rglob("*"):
                if path.is_file() and "daily_runs" in path.name:
                    log_path = path
                    break
        if log_path is None:
            return []
        last = None
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line)
            except json.JSONDecodeError:
                continue
        if not isinstance(last, dict):
            return []
        return _attention_from_log_payload(last)


def fetch_last_run(
    *,
    repo: str = DEFAULT_REPO,
    workflow: str = DEFAULT_WORKFLOW,
    artifact: str = DEFAULT_ARTIFACT,
    download_log: bool = False,
    prefer_local: bool = False,
    local_log: Path | None = None,
    gh: GhRunner | None = None,
) -> LastRunReport:
    """Return the latest scheduled daily automation run summary."""
    runner = gh or default_gh_runner
    log_path = local_log or DEFAULT_LOCAL_LOG

    if prefer_local:
        local = _parse_local_log(log_path)
        if local:
            return local
        return LastRunReport(
            source="none",
            repo=repo,
            status="none",
            conclusion=None,
            started_at=None,
            updated_at=None,
            url=None,
            detail="no local log",
        )

    run, err = _list_latest_run(repo=repo, workflow=workflow, gh=runner)
    if err is not None:
        if err.auth_unavailable:
            local = _parse_local_log(log_path)
            if local:
                local.detail = f"actions auth_unavailable; {local.detail}".strip()
                return local
        return err
    assert run is not None

    report = LastRunReport(
        source="actions",
        repo=repo,
        status=str(run.get("status") or "unknown"),
        conclusion=run.get("conclusion"),
        started_at=run.get("createdAt"),
        updated_at=run.get("updatedAt"),
        url=run.get("url"),
        display_title=run.get("displayTitle"),
        run_id=run.get("databaseId"),
    )

    if download_log and report.run_id is not None and not report.auth_unavailable:
        report.attention = _download_attention(
            repo=repo,
            run_id=report.run_id,
            artifact=artifact,
            gh=runner,
        )
    return report


def format_human(report: LastRunReport) -> str:
    lines = [
        f"ELM daily last-run  source={report.source}  repo={report.repo}",
        f"status={report.status}  conclusion={report.conclusion or '-'}",
    ]
    if report.started_at:
        lines.append(f"started={report.started_at}")
    if report.updated_at:
        lines.append(f"updated={report.updated_at}")
    if report.url:
        lines.append(f"url={report.url}")
    if report.display_title:
        lines.append(f"title={report.display_title}")
    if report.auth_unavailable or report.detail == "auth_unavailable":
        lines.append("auth_unavailable")
    if report.detail and report.detail not in {"auth_unavailable", "no runs found", "no local log"}:
        lines.append(f"detail={report.detail}")
    if report.attention:
        lines.append("attention: " + "; ".join(report.attention))
    else:
        lines.append("attention: none")
    return "\n".join(lines)


def format_json(report: LastRunReport) -> str:
    payload = asdict(report)
    return json.dumps(payload, ensure_ascii=False, indent=2)
