from typing import Any

from src.dev.domain.exceptions.base import DomainError, DomainTypeError


class InvalidExamStateError(DomainError):
    """Thrown whe an action is performed on an exam that isn't in the correct status."""

    def __init__(self, current_status: str, action: str) -> None:
        message = f"Cannot perform {action} when exam is in {current_status} status"
        super().__init__(message)


class EmptyExamReportError(DomainError):
    """Thrown when trying to sign a report without image or content."""

    def __init__(self, exam_id: Any) -> None:
        message = (
            f"Exam {exam_id} must have images or content before it can be reported"
        )
        super().__init__(message)


class InvalidFileError(DomainTypeError):
    """Trhown when a file doesn't meet DICOM or any file standards."""

    def __init__(self, filename: str, reason: str) -> None:
        message = f"File {filename!r} is not a valid DICOM or any image file: {reason}"
        super().__init__(message)
