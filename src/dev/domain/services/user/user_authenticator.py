"""Domain service for user authentication (login)"""

from src.dev.domain.entities.user import User
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import UserRepository
from src.dev.domain.ports.services.security import PasswordHasher
from src.dev.domain.value_objects.user import RawPassword, Username


class UserAuthenticatorService:
    """
    Service to verify user credentials.

    Note: session/token management belongs to the application layer.
    This service only validates credentials and returns the User entity.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def authenticate(
        self,
        username: Username,
        raw_password: RawPassword,
    ) -> User:
        """
        Authenticates a user by username and password.

        :raises DomainError: if credentials are invalid.
        """
        user = await self._user_repository.get_by_username(username)
        if user is None:
            raise DomainError("Invalid username or password.")

        is_valid = await self._password_hasher.verify(raw_password, user.password_hash)
        if not is_valid:
            raise DomainError("Invalid username or password.")

        return user
