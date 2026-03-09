"""Exam value object"""

from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class ExamCode(BaseValueObject):
    """Value object representing a exam's ID"""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Exam Code cannot be empty")
