"""Security protocols for user authentication and password hashing"""

from typing import Protocol

from src.dev.domain.entities.user import User
from src.dev.domain.value_objects.user import RawPassword, UserData, UserPasswordHash


class AuthenticationPort(Protocol):
    """Protocol for user authentication"""

    async def authenticate(self, credentials: UserData) -> User:
        """Authenticate a user with the given credentials and return the user entity"""
        ...


class PasswordHasher(Protocol):
    """Protocol for password hashing and verification"""

    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        """Hash a raw password"""
        ...

    async def verify(self, raw_password: RawPassword, hashed: UserPasswordHash) -> bool:
        """Verify a raw password against a hashed password"""
        ...
