"""Admin identity"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.user import UserRole
from src.dev.domain.value_objects.doctor import Email
from src.dev.domain.value_objects.person import PersonName
from src.dev.domain.value_objects.user import EntityID


class Admin(BaseEntity[EntityID]):
    """Represents a doctor in the system"""

    def __init__(self, *, id_: EntityID, name: PersonName, email: Email) -> None:
        super().__init__(id_=id_)
        self._name = name
        self._email = email
        self._role = UserRole.ADMIN
