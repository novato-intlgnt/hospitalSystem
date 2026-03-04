"""Report exceptions"""

from typing import Any

from src.dev.domain.exceptions.base import DomainError


class FinalizeReport(DomainError):
    """Trhown when trying to edit a report that has already been signed/finalized."""

    def __init__(self, report_id: Any) -> None:
        message = f"Report {report_id!r} is finalized and cannot be modified."
        super().__init__(message)


class UnauthorizedSignerError(DomainError):
    """Trhown when a user without a medical license tries to sign a report."""

    def __init__(self, user_id: Any, role: str) -> None:
        message = (
            f"User {user_id!r} with role {role} is not authorized to sign reports."
        )
        super().__init__(message)
