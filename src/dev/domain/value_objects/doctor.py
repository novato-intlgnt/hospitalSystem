from dataclasses import dataclass, field
from typing import Any, Self
import re

from src.dev.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class DoctorName(ValueObject):
    firstName: str
    lastName: str

    def __post_init__(self) -> None:
        if not self.firstName or not self.lastName:
            raise ValueError("First name and last name cannot be empty")

        if not self.firstName.replace(" ", "").isalpha():
            raise ValueError("First name must contain only letters")

        if not self.lastName.replace(" ", "").isalpha():
            raise ValueError("Last name must contain only letters")

        if len(self.lastName.split()) < 2:
            raise ValueError("Last name must contain at least two words")

    @property
    def fullName(self) -> str:
        return f"{self.firstName} {self.lastName}"

@dataclass(frozen=True)
class Specialty(ValueObject):
    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Specialty name cannot be empty")

@dataclass(frozen=True)
class Email(ValueObject):
    address: str 

    def __post_init__(self) -> None:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.address):
            raise ValueError(f"Invalid email format: {self.address}")

@dataclass(frozen=True)
class CMPNumber(ValueObject):
    number: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{5-6}$", self.number):
            raise ValueError(f"Invalid CMP number format: {self.number}")

@dataclass(frozen=True)
class RNENumber(ValueObject):
    number: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{5-6}$", self.number):
            raise ValueError(f"Invalid RNE number format: {self.number}")
