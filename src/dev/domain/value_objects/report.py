"""Report's value objects"""

from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject
from src.dev.domain.value_objects.exam import ExamCode


@dataclass(frozen=True)
class ReportContent(BaseValueObject):
    """Value object representing the content of a report"""

    value: str


@dataclass(frozen=True)
class ReportSignature(BaseValueObject):
    """Value object representing the signature of a report"""

    hash: bytes


@dataclass(frozen=True)
class ReportNumber(BaseValueObject):
    """Value object representing a report's ID"""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Report Number cannot be empty")


@dataclass(frozen=True)
class ReportData(BaseValueObject):
    """Value object representing report data"""

    exam_code: ExamCode
    report_num: ReportNumber
    content: ReportContent
