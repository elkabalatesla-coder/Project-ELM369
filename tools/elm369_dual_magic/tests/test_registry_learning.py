from dataclasses import asdict, FrozenInstanceError, replace
import hashlib
import json
import unittest

from tools.elm369_dual_magic import (
    ELM369DualMagicQBIT, Evidence, LearningEvent, QuestionLearningEngine,
    SourceRecord, SourceRegistry,
)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = SourceRegistry()
        self.source = SourceRecord(
            "s1", "Café example", "https://example.org", "secondary",
            "test", "2026-10-18T00:00:00Z",
        )

    def test_registration_lookup_and_json_metadata(self):
        source = replace(
            self.source, expires_at_utc="2027-01-01T00:00:00Z",
            verification_method="manual review", verified=True, notes="Caller assertion",
        )
        self.registry.register(source)
        self.assertEqual(self.registry.get("s1"), source)
        self.assertEqual(self.registry.list_sources(), [source])
        self.assertEqual(json.loads(self.registry.export_json()), [asdict(source)])
        with self.assertRaises(KeyError):
            self.registry.get("missing")

    def test_duplicate_rejected_without_overwriting(self):
        self.registry.register(self.source)
        before = self.registry.digest()
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            self.registry.register(replace(self.source, title="Replacement"))
        self.assertEqual(self.registry.get("s1"), self.source)
        self.assertEqual(before, self.registry.digest())

    def test_empty_id_rejected(self):
        for source_id in ("", " \n\t"):
            with self.subTest(source_id=source_id):
                with self.assertRaisesRegex(ValueError, "source_id is required"):
                    self.registry.register(replace(self.source, source_id=source_id))
        self.assertEqual(self.registry.list_sources(), [])

    def test_sources_sorted_and_snapshots_isolated(self):
        self.registry.register(replace(self.source, source_id="s2"))
        self.registry.register(self.source)
        sources = self.registry.list_sources()
        self.assertEqual([source.source_id for source in sources], ["s1", "s2"])
        sources.clear()
        self.assertEqual(len(self.registry.list_sources()), 2)
        with self.assertRaises(FrozenInstanceError):
            self.source.title = "Changed"
        self.assertEqual(SourceRegistry().list_sources(), [])

    def test_digest_is_canonical_order_independent_and_content_sensitive(self):
        self.registry.register(self.source)
        self.registry.register(replace(self.source, source_id="s2"))
        other = SourceRegistry()
        other.register(replace(self.source, source_id="s2"))
        other.register(self.source)
        canonical = json.dumps(
            json.loads(self.registry.export_json()), sort_keys=True,
            separators=(",", ":"), ensure_ascii=False,
        )
        self.assertEqual(
            self.registry.digest(), hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        )
        self.assertEqual(self.registry.digest(), other.digest())
        changed = SourceRegistry()
        changed.register(replace(self.source, notes="Changed"))
        changed.register(replace(self.source, source_id="s2"))
        self.assertNotEqual(self.registry.digest(), changed.digest())

    def test_registry_metadata_does_not_verify_evidence(self):
        self.registry.register(replace(self.source, verified=True))
        result = ELM369DualMagicQBIT().ask(
            "Is this claim true?", evidence=[Evidence("s1", "Claim", True)]
        )
        self.assertEqual(result.answer_kind, "insufficient_evidence")

    def test_empty_snapshot(self):
        self.assertEqual(json.loads(self.registry.export_json()), [])
        self.assertEqual(self.registry.digest(), hashlib.sha256(b"[]").hexdigest())


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.engine = QuestionLearningEngine()
        self.event = LearningEvent(
            "Is it true?", "Unknown", "insufficient_evidence", "I wanted yes",
            "evidence", "2026-10-18T00:00:00Z",
        )

    def test_feedback_stored_without_rewriting_answer_or_evidence(self):
        answer_engine = ELM369DualMagicQBIT()
        evidence = Evidence("s1", "Unverified", True)
        before = answer_engine.ask("Is it true?", evidence=[evidence])
        self.engine.record(self.event)
        self.assertEqual(self.engine.events(), [self.event])
        self.assertEqual(self.engine.events()[0].answer_kind, before.answer_kind)
        self.assertFalse(evidence.verified)
        self.assertEqual(
            answer_engine.ask("Is it true?", evidence=[evidence]).answer_kind,
            "insufficient_evidence",
        )

    def test_events_are_ordered_immutable_and_container_isolated(self):
        second = replace(self.event, user_feedback="Another observation")
        self.engine.record(self.event)
        self.engine.record(second)
        events = self.engine.events()
        self.assertEqual(events, [self.event, second])
        events.clear()
        self.assertEqual(len(self.engine.events()), 2)
        self.assertEqual(QuestionLearningEngine().events(), [])
        with self.assertRaises(FrozenInstanceError):
            self.event.answer_kind = "evidence_based_yes"

    def test_required_fields_rejected_without_recording(self):
        for field in ("question", "skill_tag"):
            for value in ("", " \n\t"):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        self.engine.record(replace(self.event, **{field: value}))
        self.assertEqual(self.engine.events(), [])

    def test_predefined_follow_ups_and_unknown_tag_fallback(self):
        for tag, fragment in {
            "evidence": "independent source", "logic": "assumption",
            "definition": "key terms", "experiment": "observable result",
            "self_reference": "What kind of answer",
        }.items():
            with self.subTest(tag=tag):
                self.assertIn(fragment, self.engine.suggest_follow_up(tag))
        self.assertEqual(
            self.engine.suggest_follow_up("unknown"),
            "What evidence or test would help evaluate this answer?",
        )

    def test_export_and_digest_include_feedback_unicode_and_event_order(self):
        self.engine.record(replace(self.event, user_feedback="Café"))
        payload = json.loads(self.engine.export_json())
        self.assertEqual(payload, [asdict(self.engine.events()[0])])
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        digest = self.engine.digest()
        self.assertEqual(digest, hashlib.sha256(canonical.encode("utf-8")).hexdigest())
        self.engine.record(self.event)
        self.assertNotEqual(digest, self.engine.digest())
        reversed_events = QuestionLearningEngine()
        for event in reversed(self.engine.events()):
            reversed_events.record(event)
        self.assertNotEqual(self.engine.digest(), reversed_events.digest())
        changed = QuestionLearningEngine()
        changed.record(replace(self.event, user_feedback="Changed"))
        self.assertNotEqual(digest, changed.digest())

    def test_empty_snapshot(self):
        self.assertEqual(json.loads(self.engine.export_json()), [])
        self.assertEqual(self.engine.digest(), hashlib.sha256(b"[]").hexdigest())


if __name__ == "__main__":
    unittest.main()
