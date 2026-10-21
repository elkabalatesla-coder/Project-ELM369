"""Separate exploratory randomness from evaluation of caller-supplied evidence."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import random
import re
from typing import Iterable, List, Optional


class Mode(str, Enum):
    RANDOM = "random"
    EVIDENCE = "evidence"


class QuestionType(str, Enum):
    YES_NO = "yes_no"
    OPEN = "open"
    SELF_REFERENTIAL = "self_referential"
    AMBIGUOUS = "ambiguous"
    COMPOUND = "compound"
    LOADED = "loaded"


@dataclass(frozen=True)
class Evidence:
    source: str
    statement: str
    supports: Optional[bool]
    verified: bool = False
    freshness: str = "unknown"

    def __post_init__(self):
        if self.supports is not None and type(self.supports) is not bool:
            raise ValueError("supports must be True, False, or None")
        if type(self.verified) is not bool:
            raise ValueError("verified must be a boolean")


@dataclass
class AnswerRecord:
    question: str
    normalized_question: str
    mode: str
    question_type: str
    answer: str
    answer_kind: str
    confidence: Optional[float]
    rationale: str
    evidence: List[dict]
    algorithm_version: str
    timestamp_utc: str
    record_sha256: str = ""


class ELM369DualMagicQBIT:
    VERSION = "1.1.0"
    RANDOM_ANSWERS = (
        "Yes",
        "No",
        "Ask a better-defined question",
        "What evidence would change your mind?",
        "Consider an alternative explanation",
        "The question may be the answer",
        "My sources say no",
    )
    _YES_NO_START = r"(?:is|are|am|was|were|do|does|did|can|could|will|would|should|has|have|had)"
    _QUESTION_START = r"(?:is|are|am|was|were|do|does|did|can|could|will|would|should|has|have|had|what|why|when|where|who|how|which)"

    def __init__(self, seed=None):
        self._rng = random.Random(seed)

    @staticmethod
    def normalize(question: str) -> str:
        return re.sub(r"\s+", " ", question.strip())

    @classmethod
    def classify(cls, question: str) -> QuestionType:
        q = cls.normalize(question).lower()
        if not q or len(q.split()) < 2:
            return QuestionType.AMBIGUOUS
        if re.search(
            r"\b(have you stopped|when did you stop|why did you)\b.*"
            r"\b(lying|cheating|stealing|making mistakes)\b", q
        ):
            return QuestionType.LOADED
        if re.search(r"\b(this question|itself|the question)\b", q) and re.search(
            r"\b(answer|question|mean|ask)\b", q
        ):
            return QuestionType.SELF_REFERENTIAL
        if q.count("?") > 1 or re.search(
            r"\b(?:and|or)\s+" + cls._QUESTION_START + r"\b", q
        ):
            return QuestionType.COMPOUND
        if q.endswith("?") and re.match(r"^" + cls._YES_NO_START + r"\b", q):
            return QuestionType.YES_NO
        if not q.endswith("?") or len(q.split()) < 4:
            return QuestionType.AMBIGUOUS
        return QuestionType.OPEN

    def ask(
        self, question: str, mode: Mode = Mode.EVIDENCE,
        evidence: Iterable[Evidence] = (),
    ) -> AnswerRecord:
        normalized = self.normalize(question)
        mode = Mode(mode)
        qtype = self.classify(normalized)
        supplied = list(evidence)
        if not normalized:
            answer, kind, confidence, rationale = (
                "Please provide a question with enough context to interpret.",
                "clarification", None, "Empty input.",
            )
        elif mode is Mode.RANDOM:
            answer, kind, confidence, rationale = (
                self._rng.choice(self.RANDOM_ANSWERS), "random_prompt", None,
                "Random exploratory selection; not evidence or a prediction.",
            )
        else:
            answer, kind, confidence, rationale = self._evidence_answer(qtype, supplied)
        payload = dict(
            question=question, normalized_question=normalized, mode=mode.value,
            question_type=qtype.value, answer=answer, answer_kind=kind,
            confidence=confidence, rationale=rationale,
            evidence=[asdict(item) for item in supplied],
            algorithm_version=self.VERSION,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return AnswerRecord(
            **payload,
            record_sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        )

    @staticmethod
    def _evidence_answer(qtype, evidence):
        if qtype is QuestionType.LOADED:
            return (
                "The question contains an unproven assumption. Restate it without presuming the claim is true.",
                "premise_check", 0.95, "Check the premise before answering.",
            )
        if qtype is QuestionType.SELF_REFERENTIAL:
            return (
                "The question may itself be part of the answer. Do you need a fact, a definition, or a logical analysis?",
                "question_as_answer", 0.90, "Self-reference does not guarantee a unique answer.",
            )
        if qtype in (QuestionType.AMBIGUOUS, QuestionType.COMPOUND):
            return (
                "Clarify the question or separate it into smaller questions.",
                "clarification", 0.90, "Input is underspecified or compound.",
            )
        if qtype is QuestionType.OPEN:
            return (
                "An open question needs a scoped explanation, not a yes/no conclusion. Specify a proposition to evaluate.",
                "clarification", None, "Evidence support flags cannot answer an open question.",
            )
        verified = [
            item for item in evidence if item.verified and item.supports is not None
        ]
        if not verified:
            return (
                "Insufficient caller-verified evidence; a reliable yes/no conclusion is not established.",
                "insufficient_evidence", 0.99, "Absence of evidence is not evidence for 'no'.",
            )
        yes = any(item.supports is True for item in verified)
        no = any(item.supports is False for item in verified)
        if yes and no:
            return (
                "The supplied sources conflict. Review source quality and context.",
                "conflicting_evidence", 0.98, "Caller-verified evidence points in opposing directions.",
            )
        if no:
            return (
                "My sources say no", "evidence_based_no", 0.85,
                "Caller-verified supplied evidence contradicts the proposition; not independently authenticated.",
            )
        return (
            "The supplied caller-verified evidence supports yes, within its stated scope.",
            "evidence_based_yes", 0.85,
            "Caller-verified supplied evidence supports the proposition; not independently authenticated.",
        )
