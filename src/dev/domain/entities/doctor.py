"""Doctor enity"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.user import UserRole
from src.dev.domain.value_objects.doctor import DoctorData
from src.dev.domain.value_objects.user import EntityID


class Doctor(BaseEntity[EntityID]):
    """Represents a doctor in the system"""

    def __init__(self, *, id_: EntityID, data: DoctorData) -> None:
        super().__init__(id_=id_)
        self._name = data.name
        self._specialty = data.specialty
        self._email = data.email
        self._cmp_number = data.cmp_number
        self._rne_number = data.rne_number
        self._role = UserRole.DOCTOR
