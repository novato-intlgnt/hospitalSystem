from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class ExamID(BaseValueObject):
    """Value object representing a patient's HC (Clinical History)"""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Exam ID cannot be empty")
