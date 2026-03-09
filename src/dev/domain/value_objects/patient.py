"""Value objects related to patient information
- DNI
- Clinical History (HC)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject
from src.dev.domain.value_objects.person import PersonName


@dataclass(frozen=True)
class PatientData(BaseValueObject):
    """Value object representing patient data"""

    dni: PatientDNI
    hc: PatientHC
    name: PersonName


@dataclass(frozen=True)
class PatientDNI(BaseValueObject):
    """Value object representing a patient's DNI (Documento Nacional de Identidad)"""

    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{8}$", self.value):
            raise ValueError(f"Invalid DNI length, must be 8 digits: {self.value}")


@dataclass(frozen=True)
class PatientHC(BaseValueObject):
    """Value object representing a patient's HC (Clinical History)"""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("PatientHC cannot be empty")
