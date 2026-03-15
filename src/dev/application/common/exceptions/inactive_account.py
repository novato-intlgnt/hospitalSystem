"""Inactive account exception for the application layer.

Business Rule: RN-16
"""

from typing import Any

from src.dev.application.common.exceptions.base import ApplicationError


class InactiveAccountError(ApplicationError):
    """Raised when an operation is attempted by or on a deactivated account.

    Business rule **RN-16**: an inactive user account must be prevented from
    authenticating or performing any system action until it is reactivated by
    an administrator.

    Args:
        user_id: The identifier of the inactive user account.
    """

    def __init__(self, user_id: Any) -> None:
        super().__init__(
            f"Account {user_id!r} is inactive and cannot perform system operations. "
            "Contact an administrator to reactivate the account."
        )
        self.user_id = user_id
