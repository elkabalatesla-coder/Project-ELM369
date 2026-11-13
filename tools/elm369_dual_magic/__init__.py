"""ELM369 Dual Magic QBIT v1.1.0: offline, rule-based prototype."""

from .engine import AnswerRecord, ELM369DualMagicQBIT, Evidence, Mode, QuestionType
from .question_learning import LearningEvent, QuestionLearningEngine
from .source_registry import SourceRecord, SourceRegistry

__all__ = [
    "AnswerRecord",
    "ELM369DualMagicQBIT",
    "Evidence",
    "Mode",
    "QuestionType",
    "LearningEvent",
    "QuestionLearningEngine",
    "SourceRecord",
    "SourceRegistry",
]
