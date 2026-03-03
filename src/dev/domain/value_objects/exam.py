"""Exam value object"""

from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject
from src.dev.domain.value_objects.user import EntityID


@dataclass(frozen=True)
class ExamID(BaseValueObject):
    """Value object representing a exam's ID"""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Exam ID cannot be empty")


@dataclass(frozen=True)
class ReportContent(BaseValueObject):
    """Value object representing the content of a report"""

    value: str


@dataclass(frozen=True)
class ReportSignature(BaseValueObject):
    """Value object representing the signature of a report"""

    hash: str
