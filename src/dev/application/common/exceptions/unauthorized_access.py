"""Unauthorized access exception for the application layer."""

from typing import Any

from src.dev.application.common.exceptions.base import ApplicationError


class UnauthorizedAccessError(ApplicationError):
    """Raised when a user attempts an action they are not permitted to perform.

    This exception is raised at the use-case level when the caller's role or
    identity does not meet the authorization requirements for the requested
    operation, independently of whether the underlying domain object exists.

    Args:
        user_id: The identifier of the user who attempted the action.
        action: A short description of the operation that was denied
                (e.g. ``"sign_report"``, ``"upload_image"``).
    """

    def __init__(self, user_id: Any, action: str) -> None:
        super().__init__(
            f"User {user_id!r} is not authorized to perform: {action!r}."
        )
        self.user_id = user_id
        self.action = action
