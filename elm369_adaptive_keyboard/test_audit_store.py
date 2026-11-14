import os
import tempfile
import unittest
from .audit_store import SQLiteAuditLedger


class SQLiteAuditLedgerTests(unittest.TestCase):
    def test_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "audit.sqlite3")
            first = SQLiteAuditLedger(path)
            first.append({"command": "help", "status": "RESOLVED"})
            second = SQLiteAuditLedger(path)
            self.assertTrue(second.verify())
            self.assertEqual(len(second.events()), 1)
            self.assertEqual(second.events()[0]["event"]["command"], "help")

    def test_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "audit.sqlite3")
            ledger = SQLiteAuditLedger(path)
            ledger.append({"command": "help"})
            with ledger._connect() as db:
                db.execute("UPDATE audit_events SET event_json=? WHERE sequence=1", ('{"command":"altered"}',))
            self.assertFalse(ledger.verify())

    def test_hash_chain_links_records(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = SQLiteAuditLedger(os.path.join(directory, "audit.sqlite3"))
            one = ledger.append({"n": 1})
            two = ledger.append({"n": 2})
            self.assertEqual(two["previous_hash"], one["event_hash"])
            self.assertTrue(ledger.verify())


if __name__ == "__main__":
    unittest.main()
