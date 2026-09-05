"""Ingest raw export files into normalized JSONL."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from tools.grok_archive.normalize import extract_backlog, iter_json_records, normalize_record
from tools.grok_archive.index import build_index

DEFAULT_VAULT = Path("vault/ELM369/JMR08241978202646902/sources")


def ingest_path(raw_path: Path, *, source: str = "grok", vault_root: Path | None = None) -> dict[str, Any]:
    root = vault_root or DEFAULT_VAULT / source
    raw_dir = root / "raw"
    norm_dir = root / "normalized"
    ext_dir = root / "extracted"
    for d in (raw_dir, norm_dir, ext_dir):
        d.mkdir(parents=True, exist_ok=True)

    files = _collect_files(raw_path)
    all_rows: list[dict[str, Any]] = []
    for f in files:
        for obj in iter_json_records(f):
            all_rows.extend(normalize_record(obj, source=source, origin=str(f.name)))

    out_norm = norm_dir / f"ingest-{source}.jsonl"
    with out_norm.open("w", encoding="utf-8") as fh:
        for row in all_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    backlog = extract_backlog(all_rows)
    out_backlog = ext_dir / f"backlog-{source}.jsonl"
    with out_backlog.open("w", encoding="utf-8") as fh:
        for item in backlog:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")

    index_stats = build_index(source=source, vault_root=root)
    return {
        "files": len(files),
        "messages": len(all_rows),
        "backlog_items": len(backlog),
        "normalized": str(out_norm),
        "backlog": str(out_backlog),
        "index": index_stats,
    }


def _collect_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".zip":
        dest = path.parent / f"{path.stem}_unzipped"
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path) as zf:
            zf.extractall(dest)
        path = dest
    if path.is_file():
        return [path]
    files: list[Path] = []
    for p in sorted(path.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".json", ".jsonl"}:
            files.append(p)
    return files


def list_normalized(source: str = "grok", vault_root: Path | None = None, limit: int = 20) -> list[dict[str, Any]]:
    root = vault_root or DEFAULT_VAULT / source
    norm = root / "normalized"
    rows: list[dict[str, Any]] = []
    if not norm.exists():
        return rows
    for f in sorted(norm.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-limit:]
