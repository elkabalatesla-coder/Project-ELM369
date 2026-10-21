"""Adapter for the repository's existing tools.elm_artifacts catalog.

This adapter registers catalog metadata only. It does not claim that the underlying
runnable files have been content-hashed or that this in-memory registry persists.
Run from the repository root so the existing catalog's relative paths resolve.
"""
from typing import Any, Dict, List

from elm369_core.registry import AppendOnlyRegistry


def register_catalog(catalog: Dict[str, Any], registry: AppendOnlyRegistry,
                    *, source_record_id: str) -> Dict[str, Any]:
    if not isinstance(catalog, dict):
        raise ValueError("catalog_must_be_object")
    if not isinstance(source_record_id, str) or not source_record_id.strip():
        raise ValueError("source_record_id_required")
    artifacts = catalog.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("catalog_artifacts_must_be_list")

    registered: List[str] = []
    for index, item in enumerate(artifacts):
        if not isinstance(item, dict):
            raise ValueError("artifact_entry_must_be_object:" + str(index))
        issue = item.get("issue")
        if issue is None or not str(issue).strip():
            raise ValueError("artifact_issue_required:" + str(index))
        artifact_id = "catalog:" + str(issue).strip()
        record = {
            "record_type": "artifact_catalog_entry",
            "source_record_id": source_record_id,
            "source": "tools.elm_artifacts.catalog",
            "catalog_index": index,
            "artifact": item,
            "content_hash_scope": "catalog_metadata_only",
        }
        registry.register(artifact_id, record)
        registered.append(artifact_id)
    return {
        "source_record_id": source_record_id,
        "catalog_count": len(artifacts),
        "registered_count": len(registered),
        "registered_ids": registered,
        "persistent": False,
        "content_hash_scope": "catalog_metadata_only",
    }


def register_repository_catalog(*, source_record_id: str) -> Dict[str, Any]:
    """Load the existing repository catalog and register its metadata in memory."""
    from tools.elm_artifacts.catalog import load, verify

    catalog = load()
    if catalog.get("error") == "missing_manifest":
        raise ValueError("existing_artifact_manifest_missing")
    verification = verify()
    registry = AppendOnlyRegistry()
    result = register_catalog(catalog, registry, source_record_id=source_record_id)
    result["existing_catalog_verification"] = verification
    result["registry_integrity_ok"] = all(
        registry.verify(record_id) for record_id in result["registered_ids"]
    )
    return result
