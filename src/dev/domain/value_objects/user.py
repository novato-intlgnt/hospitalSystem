from dataclasses import dataclass, field
from typing import Any, Self
import re

from src.dev.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class DNI(ValueObject):
    value: str = field(repr=True)

    def __post_init__(self) -> None:
        if not re.match(r"^\d{8}$", self.value):
            raise ValueError(f"Invalid DNI length, must be 8 digits: {self.value}")
@dataclass(frozen=True)
class PatientHC(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("PatientHC cannot be empty")

@dataclass(frozen=True)
class Email(ValueObject):
    address: str 

    def __post_init__(self) -> None:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.address):
            raise ValueError(f"Invalid email format: {self.address}")
