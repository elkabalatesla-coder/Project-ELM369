"""SQLite persistence for simulated financial transactions."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Iterator


def _database_path() -> Path:
    return Path(os.environ.get("ELM369_DB_PATH", "elm369_transactions.sqlite3"))


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_database() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
            """
        )


def persist_transaction(ledger: dict[str, Any]) -> int:
    """Persist a ledger and return its database identifier."""
    serialized = json.dumps(ledger, allow_nan=False, sort_keys=True)
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO transactions (ledger_json) VALUES (?)", (serialized,)
        )
        transaction_id = int(cursor.lastrowid)
    return transaction_id
