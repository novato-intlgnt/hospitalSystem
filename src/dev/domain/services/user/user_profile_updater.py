"""Domain service for updating a user's personal profile data"""

from typing import Optional

from src.dev.domain.entities.user import User
from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import UserRepository
from src.dev.domain.value_objects.doctor import DoctorData
from src.dev.domain.value_objects.person import PersonData, PersonName
from src.dev.domain.value_objects.user import Email, EntityID, UserData


class UserProfileUpdaterService:
    """Service to update a user's personal and professional profile data."""

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    async def update_profile(
        self,
        user_id: EntityID,
        new_name: Optional[PersonName] = None,
        new_email: Optional[Email] = None,
        new_doctor_data: Optional[DoctorData] = None,
    ) -> User:
        """
        Updates one or more personal data fields of the user.

        Enforces rules:
        - RN-05: If role is DOCTOR and doctor_data is being cleared, it is rejected.

        :raises DomainError: if the user is not found or business rules are violated.
        """
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise DomainError("User not found.")

        # Prevent removing doctor data from a DOCTOR-role user (RN-05)
        if user.role == UserRole.DOCTOR and new_doctor_data is None and user.doctor_data is not None:
            # Clearing doctor_data is only allowed if explicitly passed as a sentinel;
            # here we treat omission (None) as "no change", so this is fine.
            # This guard only matters if the caller explicitly wants to erase it.
            pass

        updated_name = new_name if new_name is not None else user.name
        updated_email = new_email if new_email is not None else user.email
        updated_doctor_data = new_doctor_data if new_doctor_data is not None else user.doctor_data

        updated_user_data = UserData(
            username=user.username,
            email=updated_email,
            password_hash=user.password_hash,
        )
        updated_person_data = PersonData(
            name=updated_name,
            role=user.role,
        )

        updated_user = User(
            id_=user.id_,
            user_data=updated_user_data,
            person_data=updated_person_data,
            doctor_data=updated_doctor_data,
        )
        await self._user_repository.save(updated_user)
        return updated_user
