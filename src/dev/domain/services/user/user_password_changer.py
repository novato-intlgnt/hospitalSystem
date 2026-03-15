"""Domain service for changing a user's password"""

from src.dev.domain.entities.user import User
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import UserRepository
from src.dev.domain.ports.services.security import PasswordHasher
from src.dev.domain.value_objects.person import PersonData
from src.dev.domain.value_objects.user import EntityID, RawPassword, UserData


class UserPasswordChangerService:
    """Service to handle a user's password change enforcing domain rules."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def change_password(
        self,
        user_id: EntityID,
        current_password: RawPassword,
        new_password: RawPassword,
    ) -> User:
        """
        Changes the user's password after verifying the current one.

        :raises DomainError: if the user is not found or current password is wrong.
        """
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise DomainError("User not found.")

        # Verify current password
        is_valid = await self._password_hasher.verify(current_password, user.password_hash)
        if not is_valid:
            raise DomainError("Current password is incorrect.")

        # Hash and apply the new password
        new_hash = await self._password_hasher.hash(new_password)
        updated_user_data = UserData(
            username=user.username,
            email=user.email,
            password_hash=new_hash,
        )
        updated_person_data = PersonData(
            name=user.name,
            role=user.role,
        )

        updated_user = User(
            id_=user.id_,
            user_data=updated_user_data,
            person_data=updated_person_data,
            doctor_data=user.doctor_data,
        )
        await self._user_repository.save(updated_user)
        return updated_user
