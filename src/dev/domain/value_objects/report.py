from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class ReportID(BaseValueObject):
    """Value object representing a report's ID"""

    value: str
