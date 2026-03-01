"""Exceptions to a workstation."""

from src.dev.domain.exceptions.base import DomainError


class UnauthorizedWorkstationError(DomainError):
    """Action attempted on a workstation that is not authorized."""

    def __init__(self, machine_id: str, action: str):
        message = f"The workstation {machine_id} does not have permition to: {action}."
        super().__init__(message)


class AnonymousActionBlockedError(DomainError):
    """Action attempted without an authenticated user context, which is not allowed."""

    def __init__(self):
        message = "Las terminales de visualización no permiten edición."
        super().__init__(message)
