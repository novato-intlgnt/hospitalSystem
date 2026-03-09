"""Patient entity"""

from datetime import date

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.gender import Gender
from src.dev.domain.value_objects.patient import PatientData, PatientDNI, PatientHC
from src.dev.domain.value_objects.person import PersonName
from src.dev.domain.value_objects.user import EntityID


class Patient(BaseEntity[EntityID]):
    """Patient entity representing a patient in the system."""

    def __init__(
        self,
        *,
        id_: EntityID,
        data: PatientData,
        birth_date: date,
        gender: Gender,
    ) -> None:
        super().__init__(id_=id_)
        self._hc = data.hc
        self._dni = data.dni
        self._name = data.name
        self._birth_date = birth_date
        self._gender = gender

        self.validate_invariants()

    def validate_invariants(self) -> None:
        """Validate invariants for the Patient entity."""
        if self._birth_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

    @property
    def hc(self) -> PatientHC:
        """Get the patient's Clinical History (HC) number."""
        return self._hc

    @property
    def dni(self) -> PatientDNI:
        """Get the patient's DNI."""
        return self._dni

    @property
    def name(self) -> PersonName:
        """Get the patient's name."""
        return self._name

    @property
    def birth_date(self) -> date:
        """Get the patient's birth date."""
        return self._birth_date

    @property
    def gender(self) -> Gender:
        """Get the patient's gender."""
        return self._gender
