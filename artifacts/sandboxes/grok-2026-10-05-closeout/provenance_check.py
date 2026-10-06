"""Provenance check only. Not a quantum, financial, or metaphysical engine."""
import hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
payload = {
    "id": "JMR08241978202646902",
    "anchor": "815 Tomahawk Blvd, Kokomo, Indiana 46902",
    "marker": "🌹",
}
digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
print("provenance_sha256", digest)
print("session_files", sorted(p.name for p in root.iterdir()))
