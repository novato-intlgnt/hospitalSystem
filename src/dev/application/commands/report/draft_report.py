"""Draft Report — Command Interactor

Use case: A doctor begins drafting a medical report for a completed exam.
Allowed only from REPORTING or ACQUISITION workstations (RN-05, RN-11).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

from src.dev.application.common.exceptions.invalid_machine_op import (
    InvalidMachineOperationError,
)
from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.report_gateway import ReportCommandGateway
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.workstation_gateway import WorkstationQueryGateway
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    IsDoctor,
    StandardContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.entities.report import Report
from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.report import ReportContent, ReportData, ReportNumber
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class DraftReportRequest:
    """Input DTO for DraftReportInteractor.

    Attributes:
        exam_code: Clinical code of the exam to which this report belongs.
        report_number: Administrative report number assigned by the hospital.
        content: Free-text medical findings authored by the doctor.
        doctor_id: UUID of the doctor creating the draft, resolved from the token.
        requester_ip: IPv4 address used to validate that the action originates from
            an authorized REPORTING or ACQUISITION workstation (RN-11).
    """

    exam_code: str
    report_number: str
    content: str
    doctor_id: UUID
    requester_ip: str


class DraftReportResponse(TypedDict):
    """Output DTO for DraftReportInteractor."""

    report_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class DraftReportInteractor:
    """Initiates a medical report draft linked to an exam.

    Enforced rules:
    - RN-05: Only doctors (role == MEDICO) may draft reports.
    - RN-11: The request must originate from an authorized workstation capable
      of handling legal documents (ACQUISITION or REPORTING type).
    - The draft report is in an unsigned state (version=1, no signature).

    Dependencies:
        current_user_service: Resolves and validates the authenticated actor (RN-16).
        report_command_gateway: Persists the new Report aggregate.
        workstation_query_gateway: Classifies the requesting terminal.
        flusher: Flushes ORM state before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        report_command_gateway: ReportCommandGateway,
        workstation_query_gateway: WorkstationQueryGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._report_gateway = report_command_gateway
        self._workstation_gateway = workstation_query_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: DraftReportRequest) -> DraftReportResponse:
        """Create an unsigned report draft for the given exam.

        Args:
            request: Validated input DTO with exam code, report content, and IP.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or account
                is inactive (RN-16).
            InsufficientRoleError: If the actor is not a registered doctor (RN-05).
            InvalidMachineOperationError: If the requesting workstation is not
                authorized to handle legal documents (RN-11).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            DraftReportResponse: Dictionary containing the new ``report_id``.
        """
        log.info(
            "DraftReport: started. exam_code='%s', ip='%s'.",
            request.exam_code,
            request.requester_ip,
        )

        # RN-05: Resolve and verify the acting user is a doctor.
        current_user = await self._current_user_service.get_current_user()
        authorize(IsDoctor(), context=StandardContext(subject=current_user))

        # RN-11: Validate that the station can handle legal documents.
        workstation = await self._workstation_gateway.read_by_ip(request.requester_ip)
        allowed_types = {WorkstationType.ACQUISITION, WorkstationType.REPORTING}
        if (
            workstation is None
            or not workstation["is_authorized"]
            or workstation["type"] not in allowed_types
        ):
            machine_type = str(workstation["type"]) if workstation else "UNKNOWN"
            machine_id = (
                str(workstation["id_"]) if workstation else request.requester_ip
            )
            raise InvalidMachineOperationError(
                machine_id=machine_id,
                machine_type=machine_type,
                operation="draft_report",
            )

        # Build the report aggregate (unsigned draft, version 1).
        from src.dev.domain.value_objects.doctor import DoctorID

        report_id = EntityID(value=uuid4())
        report_data = ReportData(
            exam_code=ExamCode(value=request.exam_code),
            report_num=ReportNumber(value=request.report_number),
            content=ReportContent(value=request.content),
        )
        report = Report(
            id_=report_id,
            report_data=report_data,
            doctor_id=DoctorID(value=request.doctor_id),
            version=1,
        )

        self._report_gateway.add(report)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info("DraftReport: done. report_id='%s'.", report_id.value)
        return DraftReportResponse(report_id=report_id.value)
