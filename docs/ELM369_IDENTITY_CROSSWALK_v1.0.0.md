# ELM369 Identity Crosswalk v1.0.0

**Status:** Governance reference / additive clarification  
**Effective for new records:** 2026-10-30  
**Canonical project identifier:** `JMR0824197846902`

## 1. Identifier roles

| Identifier | Role | Handling |
|---|---|---|
| `JMR0824197846902` | Canonical project identifier | Primary project anchor |
| `JMR08241978202646902` | Companion / legacy-format tracking identifier | Retain as a distinct companion identifier and provenance lineage |

The two identifiers refer to related Project ELM369 work, but they are not interchangeable identifiers. Do not silently merge, normalize, overwrite, rename, or collapse their provenance.

## 2. Anchor map

```json
{
  "project": "ELM369",
  "canonical_id": "JMR0824197846902",
  "companion_id": "JMR08241978202646902",
  "anchor_map": {
    "JMR0824197846902": "JMR0824197846902",
    "JMR08241978202646902": "JMR0824197846902"
  },
  "provenance_policy": "distinct",
  "automatic_merge": false,
  "historical_rewrite": false
}
```

The anchor map resolves both identifiers to the canonical project for navigation and association. It does **not** convert the companion identifier into the canonical identifier or authorize merging their source histories.

## 3. Record requirements

Every new project record should include:

- `project_name`
- `canonical_project_id`
- `record_identifier`
- `identifier_role` (`canonical` or `companion`)
- `source_system`
- `source_record_id`, when available
- `created_at` and `observed_at`
- `artifact_version`
- `content_sha256`, when content is stored
- `supersedes`, only when an explicit versioned correction exists
- `authorization_reference`, when a gated action is involved

A source record must retain the identifier under which it was originally created. Cross-references belong in metadata, not in destructive renaming.

## 4. Conflict handling

The audit found older repository documents that assign the two identifiers different roles from this crosswalk. This document records the current user-confirmed mapping for future work; it does not silently rewrite historical certificates, archived manifests, commit messages, or vault records.

Reconciliation procedure:

1. Preserve the original file and its blob/commit provenance.
2. Create a versioned corrected document or explicit amendment.
3. Record the original identifier, corrected role, reason, authorizing instruction, and timestamp.
4. Update active indexes and new-record templates.
5. Retain old records as historical evidence.
6. Flag unresolved references as `CONFLICT` rather than guessing.

## 5. Non-authorizations

This crosswalk does not authorize:

- Merging the two identifier histories.
- Deleting or renaming either vault path.
- Rewriting signed or historical records.
- Claiming legal ownership, registration, certification, or third-party recognition solely from an identifier or hash.
- Treating an identifier as a password, secret, or authentication credential.

## 6. Governance precedence

For newly authored ELM369 records, use this crosswalk unless a later explicitly authorized, versioned amendment supersedes it. Historical records remain evidence of what they originally stated and must be interpreted with their provenance intact.
