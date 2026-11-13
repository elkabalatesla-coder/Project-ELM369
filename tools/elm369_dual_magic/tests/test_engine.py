from dataclasses import asdict, replace
from datetime import datetime
import hashlib
import json
import unittest

from tools.elm369_dual_magic import (
    AnswerRecord, ELM369DualMagicQBIT, Evidence, Mode, QuestionType,
)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ELM369DualMagicQBIT(42)

    def test_seeded_random_is_reproducible_and_not_evidence(self):
        a = self.engine.ask("Will this work?", Mode.RANDOM)
        b = ELM369DualMagicQBIT(42).ask("Will this work?", "random")
        self.assertEqual(a.answer, b.answer)
        self.assertEqual(a.answer_kind, "random_prompt")
        self.assertIsNone(a.confidence)
        self.assertIn("not evidence or a prediction", a.rationale)
        with_evidence = ELM369DualMagicQBIT(42).ask(
            "Will this work?", Mode.RANDOM, [Evidence("s1", "No", False, True)]
        )
        self.assertEqual(a.answer, with_evidence.answer)
        self.assertEqual(with_evidence.answer_kind, "random_prompt")

    def test_normalization_and_original_input(self):
        question = " \tIs  this\nclaim true?  "
        result = self.engine.ask(question)
        self.assertEqual(result.question, question)
        self.assertEqual(result.normalized_question, "Is this claim true?")
        self.assertEqual(result.question_type, "yes_no")

    def test_classification(self):
        cases = {
            "": QuestionType.AMBIGUOUS,
            "Why?": QuestionType.AMBIGUOUS,
            "This needs more context": QuestionType.AMBIGUOUS,
            "Is this claim true?": QuestionType.YES_NO,
            "What causes the observed effect?": QuestionType.OPEN,
            "What is the answer to this question?": QuestionType.SELF_REFERENTIAL,
            "Have you stopped making mistakes?": QuestionType.LOADED,
            "When did you stop lying?": QuestionType.LOADED,
            "Why did you steal?": QuestionType.OPEN,
            "Is it safe? Will it work?": QuestionType.COMPOUND,
            "Is it safe and will it work?": QuestionType.COMPOUND,
            "Is it safe or should we wait?": QuestionType.COMPOUND,
            "What is the difference between red and blue?": QuestionType.OPEN,
            "Is salt and pepper on the table?": QuestionType.YES_NO,
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(self.engine.classify(question), expected)

    def test_question_safeguards_precede_evidence(self):
        cases = {
            "Have you stopped making mistakes?": "premise_check",
            "What is the answer to this question?": "question_as_answer",
            "Unclear": "clarification",
            "Is it safe and will it work?": "clarification",
            "What causes the observed effect?": "clarification",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                result = self.engine.ask(
                    question, evidence=[Evidence("s1", "Support", True, True)]
                )
                self.assertEqual(result.answer_kind, expected)

    def test_empty_input_is_clarified_in_both_modes(self):
        for mode in Mode:
            result = self.engine.ask(" \n\t", mode)
            self.assertEqual(result.answer_kind, "clarification")
            self.assertIsNone(result.confidence)

    def test_evidence_outcomes(self):
        positive = Evidence("positive", "Support", True, True)
        negative = Evidence("negative", "Contradiction", False, True)
        cases = [
            ([], "insufficient_evidence"),
            ([Evidence("s1", "Unverified", False)], "insufficient_evidence"),
            ([Evidence("s1", "Unverified", True)], "insufficient_evidence"),
            ([Evidence("s1", "Neutral", None, True)], "insufficient_evidence"),
            ([positive], "evidence_based_yes"),
            ([negative], "evidence_based_no"),
            ([positive, negative], "conflicting_evidence"),
            ([positive, Evidence("s1", "Unverified", False)], "evidence_based_yes"),
            ([negative, Evidence("s1", "Unverified", True)], "evidence_based_no"),
        ]
        for evidence, expected in cases:
            with self.subTest(expected=expected, evidence=evidence):
                result = self.engine.ask("Is this claim true?", evidence=iter(evidence))
                self.assertEqual(result.answer_kind, expected)
                self.assertEqual(result.mode, "evidence")
                self.assertEqual(result.evidence, [asdict(item) for item in evidence])
                if expected == "evidence_based_no":
                    self.assertEqual(result.answer, "My sources say no")

    def test_invalid_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.ask("Is this true?", "unsupported")

    def test_truthy_non_boolean_evidence_is_rejected(self):
        for value in ("false", 1, [], {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Evidence("s1", "Claim", value)
                with self.assertRaises(ValueError):
                    Evidence("s1", "Claim", True, value)

    def test_answer_digest_covers_exact_payload_and_detects_changes(self):
        evidence = Evidence("s1", "Café observation", True, True)
        result = self.engine.ask("Is this claim true?", evidence=[evidence])
        self.assertIsInstance(result, AnswerRecord)
        payload = asdict(result)
        digest = payload.pop("record_sha256")
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        self.assertEqual(digest, hashlib.sha256(canonical.encode("utf-8")).hexdigest())
        self.assertEqual(result.algorithm_version, "1.1.0")
        self.assertIsNotNone(datetime.fromisoformat(result.timestamp_utc).utcoffset())
        for field, value in [
            ("answer", "Changed"),
            ("evidence", []),
            ("question", "Changed?"),
            ("timestamp_utc", "Changed"),
        ]:
            with self.subTest(field=field):
                changed = asdict(replace(result, **{field: value}))
                changed.pop("record_sha256")
                encoded = json.dumps(
                    changed, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                ).encode("utf-8")
                self.assertNotEqual(digest, hashlib.sha256(encoded).hexdigest())

    def test_answer_evidence_is_a_snapshot(self):
        evidence = [Evidence("s1", "Support", True, True)]
        result = self.engine.ask("Is this claim true?", evidence=evidence)
        evidence.clear()
        self.assertEqual(len(result.evidence), 1)


if __name__ == "__main__":
    unittest.main()
