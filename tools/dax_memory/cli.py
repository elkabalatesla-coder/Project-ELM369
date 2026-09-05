"""CLI for DAX memory store/recall/organize."""

from __future__ import annotations

import argparse
from typing import Sequence

from tools.dax_memory import store as mem
from tools.dax_memory.index import build_index, indexed_recall
import json


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dax-memory", description="ELM369 DAX portable memory scaffolding"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    put = sub.add_parser("store", help="Store a memory entry")
    put.add_argument("content", help="Memory text")
    put.add_argument(
        "--kind",
        default="note",
        choices=sorted(mem.KINDS),
        help="Entry kind (default: note)",
    )
    put.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    put.add_argument("--confidence", type=float, default=1.0)

    get = sub.add_parser("recall", help="Recall memories by substring/tag text")
    get.add_argument("query", help="Search text")
    get.add_argument("-n", "--limit", type=int, default=10)

    ls = sub.add_parser("list", help="List recent memories")
    ls.add_argument("-n", "--limit", type=int, default=20)
    ls.add_argument("--kind", choices=sorted(mem.KINDS))
    ls.add_argument("--tag")
    ls.add_argument("--include-archived", action="store_true")

    sub.add_parser("organize", help="Deduplicate and sort the store")

    arc = sub.add_parser("archive", help="Archive a memory by id")
    arc.add_argument("memory_id")

    sub.add_parser("index", help="Rebuild inverted recall index")
    irq = sub.add_parser("irecall", help="Indexed recall (faster path)")
    irq.add_argument("query")
    irq.add_argument("-n", "--limit", type=int, default=10)

    args = parser.parse_args(argv)

    if args.command == "store":
        entry = mem.store(
            args.content,
            kind=args.kind,
            tags=args.tag,
            confidence=args.confidence,
        )
        print(f"stored {entry.memory_id} kind={entry.kind}")
        return 0

    if args.command == "recall":
        hits = mem.recall(args.query, limit=args.limit)
        if not hits:
            print("No matches.")
            return 0
        for e in hits:
            _print_entry(e)
        return 0

    if args.command == "list":
        rows = mem.list_entries(
            include_archived=args.include_archived,
            kind=args.kind,
            tag=args.tag,
            limit=args.limit,
        )
        if not rows:
            print("No memories yet.")
            return 0
        for e in rows:
            _print_entry(e)
        return 0

    if args.command == "organize":
        stats = mem.organize()
        print(
            f"organized: before={stats['before']} after={stats['after']} "
            f"removed={stats['removed']}"
        )
        return 0

    if args.command == "archive":
        entry = mem.archive(args.memory_id)
        if entry is None:
            print("Not found.")
            return 1
        print(f"archived {entry.memory_id}")
        return 0

    if args.command == "index":
        print(json.dumps(build_index(), indent=2))
        return 0

    if args.command == "irecall":
        hits = indexed_recall(args.query, limit=args.limit)
        print(json.dumps(hits, indent=2))
        return 0

    return 2


def _print_entry(e: mem.MemoryEntry) -> None:
    tags = ",".join(e.tags) if e.tags else "-"
    flag = " archived" if e.archived else ""
    print(f"{e.created_at}  {e.kind:<10}  {e.memory_id}{flag}")
    print(f"  {e.content}")
    print(f"  tags={tags} confidence={e.confidence}")
