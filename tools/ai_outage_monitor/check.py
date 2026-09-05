"""Probe configured AI services and persist JSONL records."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tools.ai_outage_monitor.classify import (
    classify_http,
    classify_statuspage_v2,
    parse_json_body,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"
DEFAULT_DATA = ROOT / "data" / "outages.jsonl"

Fetcher = Callable[[str, float], tuple[int | None, str, str | None]]


@dataclass
class ProbeResult:
    service_id: str
    name: str
    url: str
    status: str
    http_status: int | None
    detail: str
    checked_at: str


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def default_fetch(url: str, timeout: float) -> tuple[int | None, str, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "ELM369-ai-outage-monitor/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body, None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return int(exc.code), body, str(exc)
    except Exception as exc:  # noqa: BLE001
        return None, "", str(exc)


def probe_service(service: dict[str, Any], timeout: float, fetch: Fetcher) -> ProbeResult:
    url = service["url"]
    kind = service.get("kind", "http")
    code, body, err = fetch(url, timeout)
    detail = ""
    if kind == "statuspage_v2" and body:
        payload = parse_json_body(body)
        status = classify_statuspage_v2(payload, code)
        if isinstance(payload, dict):
            st = payload.get("status") or {}
            detail = str(st.get("description") or st.get("indicator") or "")
    else:
        status = classify_http(code, err)
        detail = err or (f"HTTP {code}" if code is not None else "no response")
    return ProbeResult(
        service_id=service["id"],
        name=service["name"],
        url=url,
        status=status,
        http_status=code,
        detail=detail,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def run_checks(
    config: dict[str, Any] | None = None,
    *,
    dry_run: bool = False,
    fetch: Fetcher | None = None,
    data_path: Path | None = None,
) -> list[ProbeResult]:
    cfg = config or load_config()
    timeout = float(cfg.get("timeout_seconds", 8))
    fetcher = fetch or default_fetch
    results: list[ProbeResult] = []
    for service in cfg.get("services", []):
        if dry_run:
            results.append(
                ProbeResult(
                    service_id=service["id"],
                    name=service["name"],
                    url=service["url"],
                    status="ok",
                    http_status=200,
                    detail="dry-run (no network)",
                    checked_at=datetime.now(timezone.utc).isoformat(),
                )
            )
            continue
        results.append(probe_service(service, timeout, fetcher))
    if not dry_run:
        append_records(results, data_path or DEFAULT_DATA)
    return results


def append_records(results: list[ProbeResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for item in results:
            fh.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")


def read_recent(path: Path | None = None, limit: int = 20) -> list[dict[str, Any]]:
    data_path = path or DEFAULT_DATA
    if not data_path.exists():
        return []
    lines = data_path.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
