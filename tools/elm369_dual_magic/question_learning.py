"""Feedback observations and predefined follow-ups; no training or verification."""

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import List


@dataclass(frozen=True)
class LearningEvent:
    question: str
    answer: str
    answer_kind: str
    user_feedback: str
    skill_tag: str
    created_at_utc: str


class QuestionLearningEngine:
    """Record feedback without treating preferences as factual evidence."""

    FOLLOW_UPS = {
        "evidence": "What independent source could confirm or challenge this conclusion?",
        "logic": "What assumption must be true for this conclusion to follow?",
        "definition": "What do the key terms mean in this question?",
        "experiment": "What observable result would distinguish the competing explanations?",
        "self_reference": "What kind of answer would resolve this: a fact, a definition, or another question?",
    }

    def __init__(self):
        self._events: List[LearningEvent] = []

    def record(self, event: LearningEvent) -> None:
        if not event.question.strip():
            raise ValueError("question is required")
        if not event.skill_tag.strip():
            raise ValueError("skill_tag is required")
        self._events.append(event)

    def suggest_follow_up(self, skill_tag: str) -> str:
        return self.FOLLOW_UPS.get(
            skill_tag, "What evidence or test would help evaluate this answer?"
        )

    def events(self) -> List[LearningEvent]:
        return list(self._events)

    def export_json(self) -> str:
        return json.dumps(
            [asdict(event) for event in self._events], indent=2, ensure_ascii=False
        )

    def digest(self) -> str:
        payload = json.dumps(
            [asdict(event) for event in self._events],
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
