"""Domain service for user creation"""

from typing import Optional

from src.dev.domain.entities.user import User
from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import UserRepository
from src.dev.domain.ports.services.generator import IDGenerator
from src.dev.domain.ports.services.security import PasswordHasher
from src.dev.domain.value_objects.doctor import DoctorData
from src.dev.domain.value_objects.person import PersonData
from src.dev.domain.value_objects.user import EntityID, UserData


class UserCreatorService:
    """Service to handle the creation of users enforcing domain rules."""

    def __init__(
        self,
        id_generator: IDGenerator,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._id_generator = id_generator
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def create_user(
        self,
        user_data: UserData,
        person_data: PersonData,
        doctor_data: Optional[DoctorData] = None,
    ) -> User:
        """
        Creates a new User.

        Enforces rules:
        - RN-05: A DOCTOR role user must provide doctor-specific data (CMP, RNE, specialty).
        - RN-06: Username must be unique in the system.
        """
        # Validate doctor data for DOCTOR role (RN-05)
        if person_data.role == UserRole.DOCTOR and not doctor_data:
            raise DomainError(
                "Doctor data (CMP, RNE, specialty) is required for users with DOCTOR role."
            )

        # Validate username uniqueness (RN-06)
        existing_user = await self._user_repository.get_by_username(user_data.username)
        if existing_user is not None:
            raise DomainError(
                f"A user with username '{user_data.username.value}' already exists."
            )

        # Hash the raw password and generate a new ID
        id_: EntityID = await self._id_generator.generate_id()
        hashed_password = await self._password_hasher.hash(user_data.password_hash)

        # Build final UserData with the hashed password
        secured_user_data = UserData(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
        )

        return User(
            id_=id_,
            user_data=secured_user_data,
            person_data=person_data,
            doctor_data=doctor_data,
        )
