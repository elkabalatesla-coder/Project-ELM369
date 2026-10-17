"""SQLite persistence for simulated financial transactions."""

import json
import os
from pathlib import Path
import sqlite3
from typing import Any


def _database_path() -> Path:
    return Path(os.environ.get("ELM369_DB_PATH", "elm369_transactions.sqlite3"))


def _connect() -> sqlite3.Connection:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


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
        return int(cursor.lastrowid)
