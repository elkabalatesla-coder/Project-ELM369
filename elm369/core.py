import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

PROJECT = "ELM369"
CANONICAL_ID = "JMR0824197846902"
LEGACY_ID = "JMR08241978202646902"
VERSION = "0.2.0"

MODULES = [
    {"id": "CORE-001", "name": "Identity Anchor Map", "state": "ACTIVE"},
    {"id": "INTEL-001", "name": "Rolling Logic", "state": "ACTIVE"},
    {"id": "INTEL-002", "name": "Critical Thinking Engine", "state": "ACTIVE"},
    {"id": "INTEL-003", "name": "Adaptive Observable Workflow", "state": "ACTIVE"},
    {"id": "INTEL-004", "name": "Random Protocol", "state": "DISABLED_BY_DEFAULT"},
    {"id": "INTEL-005", "name": "QBIT Scoring", "state": "ACTIVE"},
    {"id": "INTEL-006", "name": "QSTATE Model", "state": "ACTIVE"},
    {"id": "CORE-006", "name": "Evidence and Provenance", "state": "ACTIVE"},
    {"id": "CORE-007", "name": "Human Authorization Gate", "state": "ACTIVE"},
]

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_text(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def workspace():
    return Path(os.environ.get("ELM369_HOME", str(Path.home() / ".elm369"))).expanduser()

def append_audit(home, event, details):
    path = home / "logs" / "audit.jsonl"
    previous = "GENESIS"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []
    if lines:
        previous = json.loads(lines[-1])["record_sha256"]
    record = {"timestamp_utc": utc_now(), "event": event, "details": details, "previous_sha256": previous}
    record["record_sha256"] = sha256_text(canonical_json(record))
    with path.open("a", encoding="utf-8") as f:
        f.write(canonical_json(record) + "\n")
    return record["record_sha256"]

def initialize():
    home = workspace()
    for folder in ("artifacts", "checkpoints", "logs", "registry", "runs"):
        (home / folder).mkdir(parents=True, exist_ok=True)
    manifest_path = home / "baseline_manifest.json"
    if manifest_path.exists():
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        if current.get("canonical_id") != CANONICAL_ID:
            raise RuntimeError("Existing workspace identity conflict; refusing modification.")
        claimed = current.get("baseline_sha256")
        unsigned = dict(current)
        unsigned.pop("baseline_sha256", None)
        actual = sha256_text(canonical_json(unsigned))
        if claimed != actual:
            raise RuntimeError("Existing baseline manifest is damaged; refusing overwrite.")
        digest = claimed
        event = "WORKSPACE_CHECKED"
    else:
        manifest = {
            "project": PROJECT, "version": VERSION, "canonical_id": CANONICAL_ID,
            "aliases": {LEGACY_ID: CANONICAL_ID},
            "merge_policy": "FORBIDDEN_WITHOUT_EXPLICIT_OWNER_AUTHORIZATION",
            "baseline_policy": "IMMUTABLE; CHANGES MUST BE VERSIONED IN A SEPARATE LAYER",
            "random_protocol": "DISABLED_BY_DEFAULT",
            "created_utc": utc_now(), "modules": MODULES,
        }
        digest = sha256_text(canonical_json(manifest))
        manifest["baseline_sha256"] = digest
        with manifest_path.open("x", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        event = "WORKSPACE_INITIALIZED"
    (home / "logs" / "audit.jsonl").touch(exist_ok=True)
    (home / "checkpoints" / "checkpoints.jsonl").touch(exist_ok=True)
    append_audit(home, event, {"manifest_sha256": digest})
    return home

def verify():
    home = workspace()
    mp = home / "baseline_manifest.json"
    if not mp.exists():
        return False, ["Manifest missing; run init first."]
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    claimed = manifest.pop("baseline_sha256", None)
    if claimed != sha256_text(canonical_json(manifest)):
        return False, ["Baseline manifest hash mismatch."]
    audit = home / "logs" / "audit.jsonl"
    previous = "GENESIS"
    if audit.exists():
        for n, line in enumerate(audit.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            claimed_hash = record.pop("record_sha256", None)
            if record.get("previous_sha256") != previous:
                return False, [f"Audit chain link mismatch at record {n}."]
            actual_hash = sha256_text(canonical_json(record))
            if claimed_hash != actual_hash:
                return False, [f"Audit record hash mismatch at record {n}."]
            previous = claimed_hash
    return True, ["Manifest and audit chain verified."]

def checkpoint(note):
    home = workspace()
    if not (home / "baseline_manifest.json").exists():
        raise RuntimeError("Run init first.")
    manifest = json.loads((home / "baseline_manifest.json").read_text(encoding="utf-8"))
    item = {"timestamp_utc": utc_now(), "project": PROJECT, "canonical_id": CANONICAL_ID,
            "version": VERSION, "note": note, "manifest_sha256": manifest["baseline_sha256"]}
    item["checkpoint_sha256"] = sha256_text(canonical_json(item))
    with (home / "checkpoints" / "checkpoints.jsonl").open("a", encoding="utf-8") as f:
        f.write(canonical_json(item) + "\n")
    append_audit(home, "CHECKPOINT_CREATED", {"checkpoint_sha256": item["checkpoint_sha256"], "note": note})
    return item
