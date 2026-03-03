"""Patient exceptions"""

from typing import Any

from src.dev.domain.exceptions.base import DomainError


class BusinessRuleViolationEror(DomainError):
    """Generic error for specific tules (e.g., deleting a patient with active exams)."""


class PatientWithActiveExamsError(BusinessRuleViolationEror):
    """Trhown when trying to delete a patient that has active exams."""

    def __init__(self, patient_id: Any) -> None:
        message = f"Patient {patient_id!r} has active exams and cannot be deleted."
        super().__init__(message)
