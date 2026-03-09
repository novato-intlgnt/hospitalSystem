"""User entity"""

from typing import Optional

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.doctor import DoctorData
from src.dev.domain.value_objects.person import PersonData, PersonName
from src.dev.domain.value_objects.user import (
    EntityID,
    UserData,
    Username,
    Email,
    UserPasswordHash,
)


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
    def role(self) -> str:
        """Return the user's role"""
        return self._role

    @property
    def medical_credentials(self) -> str:
        """Return the doctor's credentials"""
        if not self._doctor_data:
            return "N/A"
        return (
            f"CMP: {self._doctor_data.cmp_number.number}, "
            f"RNE: {self._doctor_data.rne_number.number}"
        )

    @property
    def legal_signature(self) -> str:
        """Return the doctor's credentials"""
        if not self._doctor_data:
            return "N/A"
        return (
            f"{self._doctor_data.cmp_number.number}."
            f"{self._doctor_data.rne_number.number}"
        )

    @property
    def name(self) -> PersonName:
        """Get the user's name"""
        return self._name

    @property
    def username(self) -> Username:
        """Get the user's username"""
        return self._username

    @property
    def email(self) -> Email:
        """Get the user's email"""
        return self._email

    @property
    def password_hash(self) -> UserPasswordHash:
        """Get the user's hashed password"""
        return self._password_hash

    @property
    def doctor_data(self) -> Optional[DoctorData]:
        """Get the doctor specific data, if the user is a doctor"""
        return self._doctor_data
