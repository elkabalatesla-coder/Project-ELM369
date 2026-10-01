"""Versioned task contracts, offline providers, evaluations, and audit monitoring."""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

REGISTRY_PATH = Path("data/registries/elm369_ai_tasks.json")
AUDIT_PATH = Path("tools/elm_ai_tasks/data/runs.jsonl")
CONTRACT_VERSION = "elm369.ai_task_result.v1"
SENSITIVE_FIELD = re.compile(r"(?:password|passwd|secret|credential|api[_-]?key|access[_-]?token)", re.I)
STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been", "before",
    "being", "between", "but", "can", "could", "did", "does", "doing", "down",
    "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "here", "how", "into", "its", "just", "more", "most", "not", "off",
    "once", "only", "other", "our", "out", "over", "same", "she", "should", "some",
    "such", "than", "that", "the", "their", "them", "then", "there", "these",
    "they", "this", "those", "through", "too", "under", "until", "very", "was",
    "were", "what", "when", "where", "which", "while", "who", "will", "with",
    "would", "you", "your",
}

Provider = Callable[[Dict[str, Any]], Dict[str, Any]]
PROVIDERS: Dict[str, Provider] = {}
MODELS = {
    "builtin_rules": "keyword-frequency-v1",
    "mock": "fixed-mock-v1",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _keyword_extract(inputs: Dict[str, Any]) -> Dict[str, Any]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", inputs["text"].lower())
    counts = Counter(word.strip("'-") for word in words)
    keywords = [
        word
        for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if len(word) >= 3 and word not in STOP_WORDS
    ][:10]
    return {"keywords": keywords}


def _mock(_: Dict[str, Any]) -> Dict[str, Any]:
    return {"keywords": ["mock-result"]}


def register_provider(provider_id: str, provider: Provider, model: str) -> None:
    """Register an optional provider adapter in-process; this module performs no network I/O."""
    if not provider_id or provider_id in PROVIDERS or not callable(provider) or not model:
        raise ValueError("provider_id must be new and provider/model must be valid")
    PROVIDERS[provider_id] = provider
    MODELS[provider_id] = model


PROVIDERS.update({"builtin_rules": _keyword_extract, "mock": _mock})


def load_registry(path: Optional[Path] = None) -> Dict[str, Any]:
    registry = json.loads((path or REGISTRY_PATH).read_text(encoding="utf-8"))
    if registry.get("schema") != "elm369.ai_task_registry.v1" or not isinstance(registry.get("tasks"), list):
        raise ValueError("invalid task registry schema")
    ids = [task.get("task_id") for task in registry["tasks"]]
    if not all(isinstance(task_id, str) and task_id for task_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("task ids must be non-empty and unique")
    return registry


def list_tasks(registry_path: Optional[Path] = None) -> Dict[str, Any]:
    registry = load_registry(registry_path)
    return {
        "schema": registry["schema"],
        "version": registry["version"],
        "tasks": registry["tasks"],
    }


def _append_audit(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _audit_row(
    *,
    event: str,
    status: str,
    run_id: str,
    task_id: str,
    provider: str,
    model: str,
    registry_version: str,
    mode: str,
    audit_path: Path,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    row = {
        "event": event,
        "status": status,
        "run_id": run_id,
        "task_id": task_id,
        "provider": provider,
        "model": model,
        "registry_version": registry_version,
        "mode": mode,
        "timestamp": _now(),
    }
    if extra:
        row.update(extra)
    _append_audit(audit_path, row)


def _contains_sensitive_field(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            SENSITIVE_FIELD.search(str(key)) or _contains_sensitive_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sensitive_field(item) for item in value)
    return False


def _validate_inputs(task: Dict[str, Any], inputs: Any) -> Optional[str]:
    schema = task.get("input_schema") or {}
    if not isinstance(inputs, dict):
        return "invalid_input"
    required = schema.get("required") or []
    properties = schema.get("properties") or {}
    if any(field not in inputs for field in required):
        return "missing_input"
    if schema.get("additional_properties") is False and any(field not in properties for field in inputs):
        return "unexpected_input"
    for field, expected_type in properties.items():
        if field not in inputs:
            continue
        if expected_type == "string" and not isinstance(inputs[field], str):
            return "invalid_input_type"
    max_length = (task.get("limits") or {}).get("max_text_length")
    text = inputs.get("text")
    if max_length and isinstance(text, str) and len(text) > max_length:
        return "input_too_large"
    return None


def _validate_output(task: Dict[str, Any], output: Any) -> bool:
    if not isinstance(output, dict):
        return False
    schema = task.get("output_schema") or {}
    if any(field not in output for field in schema.get("required") or []):
        return False
    for field, expected_type in (schema.get("properties") or {}).items():
        if field not in output:
            continue
        value = output[field]
        if expected_type == "string_list" and (
            not isinstance(value, list) or any(not isinstance(item, str) for item in value)
        ):
            return False
    return True


def _find_passing_evaluation(
    task_id: str,
    provider: str,
    model: str,
    registry_version: str,
    audit_path: Path,
) -> bool:
    if not audit_path.is_file():
        return False
    for line in reversed(audit_path.read_text(encoding="utf-8").splitlines()):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            row.get("event") == "evaluation"
            and row.get("status") == "passed"
            and row.get("task_id") == task_id
            and row.get("provider") == provider
            and row.get("model") == model
            and row.get("registry_version") == registry_version
        ):
            return True
    return False


def _failure(
    error: str,
    *,
    task_id: str,
    provider: str,
    model: str,
    registry: Dict[str, Any],
    run_id: str,
    audit_path: Path,
    mode: str = "run",
) -> Dict[str, Any]:
    try:
        _audit_row(
            event="task_run",
            status="denied",
            run_id=run_id,
            task_id=task_id,
            provider=provider,
            model=model,
            registry_version=str(registry.get("version", "unknown")),
            mode=mode,
            audit_path=audit_path,
        )
    except OSError:
        return {"schema": CONTRACT_VERSION, "ok": False, "error": "audit_unavailable"}
    return {"schema": CONTRACT_VERSION, "ok": False, "error": error, "task_id": task_id}


def _execute(
    task_id: str,
    inputs: Dict[str, Any],
    *,
    provider: Optional[str],
    data_classification: str,
    human_approved: bool,
    approval_ref: Optional[str],
    registry_path: Optional[Path],
    audit_path: Path,
    evaluation_mode: bool,
) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    try:
        registry = load_registry(registry_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"schema": CONTRACT_VERSION, "ok": False, "error": "registry_unavailable"}
    task = next((item for item in registry["tasks"] if item["task_id"] == task_id), None)
    selected_provider = provider or (task or {}).get("default_provider", "")
    model = MODELS.get(selected_provider, "unknown")
    mode = "evaluation" if evaluation_mode else "run"
    if task is None:
        return _failure(
            "unknown_task", task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    if selected_provider not in (task.get("providers") or []) or selected_provider not in PROVIDERS:
        return _failure(
            "provider_unavailable", task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    if _contains_sensitive_field(inputs):
        return _failure(
            "sensitive_input_field", task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    input_error = _validate_inputs(task, inputs)
    if input_error:
        return _failure(
            input_error, task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    if data_classification not in (task.get("allowed_data_classifications") or []):
        return _failure(
            "data_classification_not_allowed", task_id=task_id, provider=selected_provider,
            model=model, registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    approval_required = bool(task.get("consequential") or task.get("requires_human_approval"))
    if approval_required and not (human_approved and isinstance(approval_ref, str) and approval_ref.strip()):
        return _failure(
            "human_approval_required", task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )
    if task.get("evaluation_required") and not evaluation_mode and not _find_passing_evaluation(
        task_id, selected_provider, model, str(registry["version"]), audit_path
    ):
        return _failure(
            "evaluation_required", task_id=task_id, provider=selected_provider, model=model,
            registry=registry, run_id=run_id, audit_path=audit_path, mode=mode,
        )

    try:
        _audit_row(
            event="task_run",
            status="started",
            run_id=run_id,
            task_id=task_id,
            provider=selected_provider,
            model=model,
            registry_version=str(registry["version"]),
            mode=mode,
            audit_path=audit_path,
        )
    except OSError:
        return {"schema": CONTRACT_VERSION, "ok": False, "error": "audit_unavailable"}

    try:
        output = PROVIDERS[selected_provider](inputs)
        if not _validate_output(task, output):
            raise ValueError("invalid provider output")
    except Exception:
        try:
            _audit_row(
                event="task_run", status="failed", run_id=run_id, task_id=task_id,
                provider=selected_provider, model=model, registry_version=str(registry["version"]),
                mode=mode, audit_path=audit_path,
            )
        except OSError:
            return {"schema": CONTRACT_VERSION, "ok": False, "error": "audit_unavailable"}
        return {"schema": CONTRACT_VERSION, "ok": False, "error": "provider_failed", "task_id": task_id}

    try:
        _audit_row(
            event="task_run",
            status="succeeded",
            run_id=run_id,
            task_id=task_id,
            provider=selected_provider,
            model=model,
            registry_version=str(registry["version"]),
            mode=mode,
            audit_path=audit_path,
            extra={"human_approved": bool(approval_required and human_approved)},
        )
    except OSError:
        return {"schema": CONTRACT_VERSION, "ok": False, "error": "audit_unavailable"}

    return {
        "schema": CONTRACT_VERSION,
        "ok": True,
        "task_id": task_id,
        "output": output,
        "provenance": {
            "run_id": run_id,
            "registry_version": str(registry["version"]),
            "provider": selected_provider,
            "model": model,
            "offline": True,
            "data_classification": data_classification,
            "human_approved": bool(approval_required and human_approved),
            "lifecycle": task.get("lifecycle", "sandbox"),
            "executed_at": _now(),
        },
    }


def execute(
    task_id: str,
    inputs: Dict[str, Any],
    *,
    provider: Optional[str] = None,
    data_classification: str = "internal",
    human_approved: bool = False,
    approval_ref: Optional[str] = None,
    registry_path: Optional[Path] = None,
    audit_path: Optional[Path] = None,
) -> Dict[str, Any]:
    return _execute(
        task_id, inputs, provider=provider, data_classification=data_classification,
        human_approved=human_approved, approval_ref=approval_ref, registry_path=registry_path,
        audit_path=audit_path or AUDIT_PATH, evaluation_mode=False,
    )


def evaluate(
    task_id: str,
    *,
    provider: Optional[str] = None,
    human_approved: bool = False,
    approval_ref: Optional[str] = None,
    registry_path: Optional[Path] = None,
    audit_path: Optional[Path] = None,
) -> Dict[str, Any]:
    audit = audit_path or AUDIT_PATH
    try:
        registry = load_registry(registry_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"ok": False, "error": "registry_unavailable"}
    task = next((item for item in registry["tasks"] if item["task_id"] == task_id), None)
    if task is None:
        return {"ok": False, "error": "unknown_task", "task_id": task_id}
    selected_provider = provider or task.get("default_provider", "")
    cases = task.get("evaluation_cases") or []
    if not cases:
        return {"ok": False, "error": "evaluation_cases_missing", "task_id": task_id}
    results = []
    for case in cases:
        result = _execute(
            task_id,
            case.get("input"),
            provider=selected_provider,
            data_classification="public",
            human_approved=human_approved,
            approval_ref=approval_ref,
            registry_path=registry_path,
            audit_path=audit,
            evaluation_mode=True,
        )
        expected = (case.get("expected_outputs") or {}).get(
            selected_provider, case.get("expected_output")
        )
        results.append(bool(result.get("ok") and result.get("output") == expected))
    passed = sum(results)
    model = MODELS.get(selected_provider, "unknown")
    evaluation_id = str(uuid.uuid4())
    try:
        _audit_row(
            event="evaluation",
            status="passed" if passed == len(results) else "failed",
            run_id=evaluation_id,
            task_id=task_id,
            provider=selected_provider,
            model=model,
            registry_version=str(registry["version"]),
            mode="evaluation",
            audit_path=audit,
            extra={
                "cases": len(results),
                "passed_cases": passed,
                "accuracy": passed / len(results),
                "human_approved": bool(human_approved),
            },
        )
    except OSError:
        return {"ok": False, "error": "audit_unavailable", "task_id": task_id}
    return {
        "ok": passed == len(results),
        "task_id": task_id,
        "provider": selected_provider,
        "model": model,
        "registry_version": str(registry["version"]),
        "cases": len(results),
        "passed_cases": passed,
        "accuracy": passed / len(results),
        "evaluation_id": evaluation_id,
    }


def monitor(audit_path: Optional[Path] = None) -> Dict[str, Any]:
    path = audit_path or AUDIT_PATH
    counts = Counter()
    by_task: Dict[str, Counter] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            event = row.get("event", "unknown")
            status = row.get("status", "unknown")
            counts[event + ":" + status] += 1
            task_counts = by_task.setdefault(str(row.get("task_id", "unknown")), Counter())
            task_counts[event + ":" + status] += 1
    return {
        "schema": "elm369.ai_task_monitor.v1",
        "audit_available": path.is_file(),
        "counts": dict(sorted(counts.items())),
        "by_task": {key: dict(sorted(value.items())) for key, value in sorted(by_task.items())},
    }
