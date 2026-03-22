from src.dev.application.common.exceptions.base import ApplicationError


class InsufficientRoleError(ApplicationError):
    """
    Raised when an authenticated user attempts to perform an action that
    is strictly beyond their assigned Role privileges (e.g., a Tech trying
    to create another user account, which is an Admin-only function).
    """

    def __init__(
        self, message: str = "Insufficient permissions to perform this action."
    ) -> None:
        super().__init__(message=message)
