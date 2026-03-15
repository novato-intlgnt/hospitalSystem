"""Immutable report exception for the application layer.

Business Rule: RN-06
"""

from typing import Any

from src.dev.application.common.exceptions.base import ApplicationError


class ImmutableReportError(ApplicationError):
    """Raised when a modification is attempted on a finalized (signed) report.

    Business rule **RN-06**: once a radiological report has been signed and
    delivered it becomes legally immutable.  Any subsequent attempt to edit,
    delete, or re-sign the report must be rejected at the use-case level.

    Args:
        report_id: The identifier of the finalized report.
    """

    def __init__(self, report_id: Any) -> None:
        super().__init__(
            f"Report {report_id!r} has been finalized and is legally immutable. "
            "No modifications are permitted."
        )
        self.report_id = report_id
