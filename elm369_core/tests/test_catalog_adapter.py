import unittest

from elm369_core.catalog_adapter import register_catalog, register_repository_catalog
from elm369_core.registry import AppendOnlyRegistry


class CatalogAdapterTests(unittest.TestCase):
    def test_registers_catalog_metadata_without_claiming_persistence(self):
        registry = AppendOnlyRegistry()
        result = register_catalog(
            {"artifacts": [
                {"issue": 25, "title": "Translator", "runnable": "tools/elm_translator"},
                {"issue": 26, "title": "Diagnostics", "runnable": "tools/diagnostics"},
            ]},
            registry,
            source_record_id="test-catalog-v1",
        )
        self.assertEqual(result["registered_count"], 2)
        self.assertFalse(result["persistent"])
        self.assertEqual(result["content_hash_scope"], "catalog_metadata_only")
        self.assertTrue(registry.verify("catalog:25"))
        self.assertTrue(registry.verify("catalog:26"))

    def test_rejects_catalog_entries_without_issue_id(self):
        with self.assertRaisesRegex(ValueError, "artifact_issue_required"):
            register_catalog({"artifacts": [{"title": "No ID"}]},
                             AppendOnlyRegistry(), source_record_id="fixture")

    def test_duplicate_issue_id_is_rejected_by_append_only_registry(self):
        with self.assertRaisesRegex(ValueError, "immutable_record_id_exists"):
            register_catalog({"artifacts": [
                {"issue": 25}, {"issue": 25}
            ]}, AppendOnlyRegistry(), source_record_id="fixture")

    def test_repository_artifact_catalog_adapter_smoke(self):
        result = register_repository_catalog(source_record_id="repository-catalog-smoke")
        self.assertGreater(result["catalog_count"], 0)
        self.assertEqual(result["catalog_count"], result["registered_count"])
        self.assertTrue(result["registry_integrity_ok"])
        self.assertTrue(result["existing_catalog_verification"]["ok"])


if __name__ == "__main__":
    unittest.main()
