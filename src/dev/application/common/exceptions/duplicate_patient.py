"""Duplicate patient exception for the application layer."""

from src.dev.application.common.exceptions.base import ApplicationError


class DuplicatePatientError(ApplicationError):
    """Raised when a new patient conflicts with an already-registered patient record.

    The uniqueness constraint is enforced at the use-case level before
    persisting a new patient.  A patient is considered a duplicate when
    another record with the same DNI or Clinical History (HC) number already
    exists in the system.

    Args:
        field: The field that triggered the conflict
               (e.g. ``"dni"``, ``"hc"``).
        value: The conflicting field value.
    """

    def __init__(self, field: str, value: str) -> None:
        super().__init__(
            f"A patient with {field.upper()} {value!r} is already registered in the system."
        )
        self.field = field
        self.value = value
