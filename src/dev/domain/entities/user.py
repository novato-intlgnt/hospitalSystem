"""User entity"""

from typing import Optional

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.doctor import DoctorData
from src.dev.domain.value_objects.person import PersonData
from src.dev.domain.value_objects.user import EntityID, UserData


class User(BaseEntity[EntityID]):
    """Represents a system's user, which can be either a doctor or an admin"""

    def __init__(
        self,
        *,
        id_: EntityID,
        user_data: UserData,
        person_data: PersonData,
        doctor_data: Optional[DoctorData] = None,
    ) -> None:
        super().__init__(id_=id_)
        self._name = person_data.name
        self._username = user_data.username
        self._email = user_data.email
        self._password_hash = user_data.password_hash
        self._role = person_data.role
        self._doctor_data = doctor_data

    @property
    def is_doctor(self) -> bool:
        """Check if the user is a doctor"""
        return self._role == "DOCTOR"

    @property
    def medical_credentials(self) -> str:
        """Return the doctor's credentials"""
        if not self._doctor_data:
            return "N/A"
        return (
            f"CMP: {self._doctor_data.cmp_number.number}, "
            f"RNE: {self._doctor_data.rne_number.number}"
        )
