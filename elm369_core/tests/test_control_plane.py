import unittest

from elm369_core.audit import build_chain, verify_chain
from elm369_core.dependency import DependencyError, topological_order
from elm369_core.identity import CANONICAL_ANCHOR, COMPANION_ANCHOR, resolve_identity
from elm369_core.lifecycle import LifecycleError, advance
from elm369_core.registry import AppendOnlyRegistry


class IdentityTests(unittest.TestCase):
    def test_alias_resolves_without_losing_origin(self):
        canonical = resolve_identity(CANONICAL_ANCHOR, source_record_id="r1", provenance={"source": "doc-a"})
        companion = resolve_identity(COMPANION_ANCHOR, source_record_id="r2", provenance={"source": "doc-b"})
        self.assertEqual(canonical["canonical_anchor"], companion["canonical_anchor"])
        self.assertEqual(canonical["submitted_identifier"], CANONICAL_ANCHOR)
        self.assertEqual(companion["submitted_identifier"], COMPANION_ANCHOR)
        self.assertNotEqual(canonical["provenance"], companion["provenance"])
        self.assertFalse(companion["provenance_merge_permitted"])

    def test_identity_provenance_is_detached(self):
        provenance = {"source": {"file": "identity.md"}}
        record = resolve_identity(CANONICAL_ANCHOR, source_record_id="r1", provenance=provenance)
        provenance["source"]["file"] = "changed.md"
        self.assertEqual(record["provenance"]["source"]["file"], "identity.md")

    def test_unknown_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown_project_identifier"):
            resolve_identity("unknown", source_record_id="r1", provenance={"source": "x"})


class DependencyTests(unittest.TestCase):
    def test_stable_topological_order(self):
        self.assertEqual(topological_order({"api": ["service"], "service": ["schema"], "schema": []}),
                         ["schema", "service", "api"])

    def test_missing_dependency_and_cycle_rejected(self):
        with self.assertRaisesRegex(DependencyError, "missing_dependencies"):
            topological_order({"api": ["missing"]})
        with self.assertRaisesRegex(DependencyError, "dependency_cycle"):
            topological_order({"a": ["b"], "b": ["a"]})


class LifecycleTests(unittest.TestCase):
    def test_missing_evidence_blocks_transition(self):
        with self.assertRaisesRegex(LifecycleError, "missing_evidence"):
            advance("SNAPSHOT")

    def test_canary_requires_human_authorization(self):
        with self.assertRaisesRegex(LifecycleError, "human_authorization_required"):
            advance("AUTHORIZATION", evidence=["authorization_record"], authorized=False)

    def test_reject_is_terminal(self):
        self.assertEqual(advance("PROPOSE", reject=True), "REJECTED")
        with self.assertRaisesRegex(LifecycleError, "terminal_state"):
            advance("REJECTED")


class RegistryTests(unittest.TestCase):
    def test_register_verify_and_prevent_duplicate_id(self):
        registry = AppendOnlyRegistry()
        record = registry.register("artifact-1", {"version": "1.0.0", "status": "PROPOSED"})
        self.assertTrue(registry.verify("artifact-1"))
        self.assertEqual(len(record["sha256"]), 64)
        with self.assertRaisesRegex(ValueError, "immutable_record_id_exists"):
            registry.register("artifact-1", {"version": "1.0.1"})

    def test_nested_input_mutation_does_not_change_registered_record(self):
        registry = AppendOnlyRegistry()
        source = {"metadata": {"version": "1.0.0"}}
        registry.register("artifact-2", source)
        source["metadata"]["version"] = "9.9.9"
        self.assertTrue(registry.verify("artifact-2"))
        self.assertEqual(registry.get("artifact-2")["record"]["metadata"]["version"], "1.0.0")

    def test_returned_record_mutation_does_not_change_registered_record(self):
        registry = AppendOnlyRegistry()
        returned = registry.register("artifact-3", {"metadata": {"version": "1.0.0"}})
        returned["record"]["metadata"]["version"] = "9.9.9"
        self.assertTrue(registry.verify("artifact-3"))


class AuditTests(unittest.TestCase):
    def test_hash_chain_and_tamper_detection(self):
        chain = build_chain([
            {"event_id": "e1", "event_type": "SNAPSHOT", "payload": {"sha": "abc"}},
            {"event_id": "e2", "event_type": "TEST", "payload": {"result": "PASS"}},
        ])
        self.assertTrue(verify_chain(chain))
        changed = [dict(item) for item in chain]
        changed[0]["payload"] = {"sha": "tampered"}
        self.assertFalse(verify_chain(changed))


if __name__ == "__main__":
    unittest.main()
