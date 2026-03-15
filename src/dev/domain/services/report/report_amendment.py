"""
Domain Service: ReportAmendmentService
"""

from src.dev.domain.entities.report import Report
from src.dev.domain.value_objects.report import ReportContent
from src.dev.domain.value_objects.user import EntityID


class ReportAmendmentService:
    """
    Domain Service that encapsulates the business logic for versioning and amending medical reports.
    RN-06: Versionado de informes
    """

    def amend_report(
        self, original_report: Report, new_id: EntityID, new_content: ReportContent
    ) -> Report:
        """
        Amends a finalized report, generating a new version of it.
        This orchestration uses the Entity's native `create_amendment` method, avoiding redundant logic.
        """
        # Rely on the Entity to enforce rules:
        new_report = original_report.create_amendment(
            new_id=new_id, new_content=new_content
        )

        return new_report
