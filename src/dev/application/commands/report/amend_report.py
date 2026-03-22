"""Amend Report — Command Interactor

Use case: A doctor issues a corrected version of an already-signed report.
The original report is immutable; this creates a new amendment version (RN-06).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

from src.dev.application.common.exceptions.immutable_report import ImmutableReportError
from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.report_gateway import ReportCommandGateway
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    IsDoctor,
    StandardContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.report import ReportContent
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class AmendReportRequest:
    """Input DTO for AmendReportInteractor.

    Attributes:
        report_id: Unique identifier of the signed (final) report to be amended.
        new_content: Corrected medical content that will replace the original
            in the new amendment version.
    """

    report_id: UUID
    new_content: str


class AmendReportResponse(TypedDict):
    """Output DTO for AmendReportInteractor."""

    new_report_id: UUID
    version: int


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class AmendReportInteractor:
    """Creates a corrected amendment of a previously signed report.

    Enforced rules:
    - RN-05: Only doctors may amend reports.
    - RN-06: The original signed report remains immutable; ``Report.create_amendment``
      returns a *new* Report instance (next version, same exam, no signature).
      Attempting to amend a draft (unsigned) report raises ``ValueError``.

    Dependencies:
        current_user_service: Resolves authenticated actor and verifies account
            is active (RN-16).
        report_command_gateway: Hydrates the source report and persists the amendment.
        flusher: Flushes ORM state before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        report_command_gateway: ReportCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._report_gateway = report_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: AmendReportRequest) -> AmendReportResponse:
        """Produce a new amendment version of a signed report.

        Args:
            request: DTO containing the signed ``report_id`` and ``new_content``.

        Raises:
            UnauthorizedAccessError: If the actor's session is invalid or inactive.
            InsufficientRoleError: If the actor is not a registered doctor (RN-05).
            DomainError: If the target report is not found.
            ValueError: If the target report is not yet signed — only final reports
                can be amended (RN-06).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            AmendReportResponse: Dictionary with ``new_report_id`` and ``version``.
        """
        log.info("AmendReport: started. source_report_id='%s'.", request.report_id)

        # RN-05: Verify the actor is a registered doctor.
        current_user = await self._current_user_service.get_current_user()
        authorize(IsDoctor(), context=StandardContext(subject=current_user))

        # Hydrate source report with an exclusive lock for the amendment transaction.
        source_report_id = EntityID(value=request.report_id)
        source_report = await self._report_gateway.read_by_id(
            source_report_id, for_update=True
        )
        if source_report is None:
            raise DomainError(f"Report '{request.report_id}' not found.")

        # RN-06: Domain entity enforces that only final reports can be amended.
        new_report_id = EntityID(value=uuid4())
        amended_report = source_report.create_amendment(
            new_id=new_report_id,
            new_content=ReportContent(value=request.new_content),
        )

        self._report_gateway.add(amended_report)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "AmendReport: done. new_report_id='%s', version=%d.",
            new_report_id.value,
            amended_report.version,
        )
        return AmendReportResponse(
            new_report_id=new_report_id.value,
            version=amended_report.version,
        )
