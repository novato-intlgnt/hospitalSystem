"""Report status"""

from enum import StrEnum


class ReportStatus(StrEnum):
    """Status of the report in the workflow"""

    DRAFT = "DRAFT"
    SIGNED = "SIGNED"
