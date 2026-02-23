"""Value objects related to the Doctor entity"""

import re
from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject
from src.dev.domain.value_objects.person import PersonName


@dataclass(frozen=True)
class DoctorData(BaseValueObject):
    """Value object representing the doctor's data"""

    name: PersonName
    specialty: Specialty
    email: Email
    cmp_number: CMPNumber
    rne_number: RNENumber


@dataclass(frozen=True)
class Specialty(BaseValueObject):
    """Value object representing a medical Specialty"""

    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Specialty name cannot be empty")


@dataclass(frozen=True)
class Email(BaseValueObject):
    """Value object representing an email address"""

    address: str

    def __post_init__(self) -> None:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.address):
            raise ValueError(f"Invalid email format: {self.address}")


@dataclass(frozen=True)
class CMPNumber(BaseValueObject):
    """Value object representing a CMP (Colegio Médico del Perú) number"""

    number: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{5-6}$", self.number):
            raise ValueError(f"Invalid CMP number format: {self.number}")


@dataclass(frozen=True)
class RNENumber(BaseValueObject):
    """Value object representing an RNE (Registro Nacional de Especialistas) number"""

    number: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{5-6}$", self.number):
            raise ValueError(f"Invalid RNE number format: {self.number}")
