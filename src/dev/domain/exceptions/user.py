"""Exceptions related to user management."""

from typing import Any

from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.user import EntityID, Username


class UsernameAlreadyExistsError(DomainError):
    """Trhown when trying to create a user with a username that already exists in the system."""

    def __init__(self, username: Any) -> None:
        message = f"User with {username!r} already exists."
        super().__init__(message)


class UserNotFoundByIdError(DomainError):
    """Trhown when trying to access a user that doesn't exist in the system by its ID."""

    def __init__(self, user_id: EntityID) -> None:
        message = f"User with {user_id.value!r} is not found."
        super().__init__(message)


class UserNotFoundByUsernameError(DomainError):
    """Trhown when trying to access a user that doesn't exist in the system by its username."""

    def __init__(self, username: Username) -> None:
        message = f"User with {username.value!r} is not found."
        super().__init__(message)


class ActivationChangeNotPermittedError(DomainError):
    """Trhown when trying to change activation of a user that isn't allowed to be changed."""

    def __init__(self, username: Username, role: UserRole) -> None:
        message = (
            f"Changing activation of user {username.value!r} ({role}) is not permitted."
        )
        super().__init__(message)


class RoleAssignmentNotPermittedError(DomainError):
    """Trhown when trying to assign a role to a user that is not allowed to be assigned."""

    def __init__(self, role: UserRole) -> None:
        message = f"Assignment of role {role} is not permitted."
        super().__init__(message)


class RoleChangeNotPermittedError(DomainError):
    """Trhown when trying to change the role of a user that is not allowed to be changed."""

    def __init__(self, username: Username, role: UserRole) -> None:
        message = f"Changing role of user {username.value!r} ({role}) is not permitted."
        super().__init__(message)
