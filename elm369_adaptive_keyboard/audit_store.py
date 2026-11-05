"""SQLite-backed append-only hash-chain audit ledger for local ELM369 use."""
import json
import sqlite3
import threading
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Dict


class SQLiteAuditLedger:
    """Durable local ledger. Hash chain detects edits but is not a signed external timestamp."""
    def __init__(self, path="elm369_audit.sqlite3"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._session() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS audit_events (
                sequence INTEGER PRIMARY KEY,
                previous_hash TEXT NOT NULL,
                event_json TEXT NOT NULL,
                event_hash TEXT NOT NULL
            )""")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5.0)
        db.row_factory = sqlite3.Row
        return db

    @contextmanager
    def _session(self):
        db = self._connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def append(self, event: Dict[str, object]) -> Dict[str, object]:
        event_json = self._canonical(event)
        with self._lock, self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT sequence,event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1").fetchone()
            sequence = 1 if row is None else row["sequence"] + 1
            previous_hash = "0" * 64 if row is None else row["event_hash"]
            body = {"sequence": sequence, "previous_hash": previous_hash, "event": json.loads(event_json)}
            digest = sha256(self._canonical(body).encode("utf-8")).hexdigest()
            db.execute("INSERT INTO audit_events(sequence,previous_hash,event_json,event_hash) VALUES(?,?,?,?)",
                       (sequence, previous_hash, event_json, digest))
        return dict(body, event_hash=digest)

    def verify(self) -> bool:
        previous = "0" * 64
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT sequence,previous_hash,event_json,event_hash FROM audit_events ORDER BY sequence").fetchall()
        for expected_sequence, row in enumerate(rows, start=1):
            if row["sequence"] != expected_sequence or row["previous_hash"] != previous:
                return False
            try:
                event = json.loads(row["event_json"])
            except (TypeError, json.JSONDecodeError):
                return False
            body = {"sequence": expected_sequence, "previous_hash": previous, "event": event}
            digest = sha256(self._canonical(body).encode("utf-8")).hexdigest()
            if digest != row["event_hash"]:
                return False
            previous = digest
        return True

    def events(self):
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT sequence,previous_hash,event_json,event_hash FROM audit_events ORDER BY sequence").fetchall()
        return tuple({"sequence": row["sequence"], "previous_hash": row["previous_hash"],
                      "event": json.loads(row["event_json"]), "event_hash": row["event_hash"]}
                     for row in rows)
