"""CLI for Grok archive intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.grok_archive.ingest import ingest_path, list_normalized
from tools.grok_archive.status import vault_status
from tools.grok_archive.index import build_index, search
from tools.grok_archive.normalize import extract_backlog


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="grok-archive", description="ELM369 Grok/discussion archive intake")
    sub = parser.add_subparsers(dest="command", required=True)

    ing = sub.add_parser("ingest", help="Ingest raw JSON/JSONL/ZIP exports")
    ing.add_argument("--path", required=True, help="File or directory of raw exports")
    ing.add_argument("--source", default="grok", help="Source provider folder name (default: grok)")

    ls = sub.add_parser("list", help="List recent normalized messages")
    ls.add_argument("--source", default="grok")
    ls.add_argument("-n", "--limit", type=int, default=20)

    ex = sub.add_parser("extract-backlog", help="Re-extract design/dev backlog from normalized JSONL")
    ex.add_argument("--source", default="grok")

    st = sub.add_parser("status", help="Multi-source vault status summary")
ix = sub.add_parser("index", help="Rebuild inverted search index")
    ix.add_argument("--source", default="grok")

    se = sub.add_parser("search", help="Search normalized + backlog via inverted index")
    se.add_argument("query")
    se.add_argument("--source", default="grok")
    se.add_argument("-n", "--limit", type=int, default=20)

    args = parser.parse_args(argv)

    if args.command == "ingest":
        stats = ingest_path(Path(args.path), source=args.source)
        print(json.dumps(stats, indent=2))
        return 0

    if args.command == "list":
        rows = list_normalized(source=args.source, limit=args.limit)
        if not rows:
            print("No normalized messages yet. Drop exports in vault/.../sources/grok/raw and run ingest.")
            return 0
        for r in rows:
            print(f"{r.get('role','?'):<12} {str(r.get('content',''))[:120]}")
        return 0

    if args.command == "status":
        print(json.dumps(vault_status(), indent=2))
        return 0

    if args.command == "index":
        print(json.dumps(build_index(source=args.source), indent=2))
        return 0

    if args.command == "search":
        hits = search(args.query, source=args.source, limit=args.limit)
        print(json.dumps(hits, indent=2))
        return 0

    if args.command == "extract-backlog":
        root = Path("vault/ELM369/JMR08241978202646902/sources") / args.source
        rows = []
        for f in (root / "normalized").glob("*.jsonl"):
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        backlog = extract_backlog(rows)
        out = root / "extracted" / f"backlog-{args.source}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            for item in backlog:
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"wrote {len(backlog)} items -> {out}")
        return 0

    return 2
