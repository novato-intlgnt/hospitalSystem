"""Patient entity"""

from datetime import date

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.gender import Gender
from src.dev.domain.value_objects.patient import PatientData
from src.dev.domain.value_objects.user import EntityID


class Patient(BaseEntity[EntityID]):
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
        self._patient_id = data.patient_id
        self._dni = data.dni
        self._name = data.name
        self._birth_date = birth_date
        self._gender = gender
