"""Sign Report — Command Interactor

Use case: A doctor finalizes and cryptographically signs a drafted report,
making it legally immutable (RN-06, RN-07, RN-16).
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TypedDict
from uuid import UUID

from src.dev.application.common.exceptions.immutable_report import ImmutableReportError
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
from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class SignReportRequest:
    """Input DTO for SignReportInteractor.

    Attributes:
        report_id: Unique identifier of the draft report to be signed.
        requester_ip: IPv4 address of the station — must be ACQUISITION or
            REPORTING type for the action to be allowed (RN-16).
    """

    report_id: UUID
    requester_ip: str


class SignReportResponse(TypedDict):
    """Output DTO for SignReportInteractor."""

    report_id: UUID
    signed_at: str  # ISO-8601 timestamp of when the signing was recorded.


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class SignReportInteractor:
    """Finalizes a report by applying the doctor's legal signature.

    Enforced rules:
    - RN-05: Signing actor must hold the MEDICO role with valid credentials.
    - RN-06: Once signed, the report is immutable — ``Report.sign`` raises
      ``FinalizeReport`` if a second signing is attempted on the same version.
    - RN-07: The legal signature embeds the doctor's CMP and RNE identifiers.
    - RN-16: The request must originate from an authorized ACQUISITION or
      REPORTING workstation; the actor's account must also be active.

    Dependencies:
        current_user_service: Resolves authenticated actor; enforces RN-16.
        report_command_gateway: Hydrates and persists the Report aggregate.
        workstation_query_gateway: Validates the requesting terminal classification.
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

    async def execute(self, request: SignReportRequest) -> SignReportResponse:
        """Sign the report with the doctor's legal credentials.

        Args:
            request: DTO with ``report_id`` and ``requester_ip``.

        Raises:
            UnauthorizedAccessError: If the actor token is invalid or account
                is inactive (RN-16).
            InsufficientRoleError: If the actor is not a doctor or lacks
                CMP/RNE credentials (RN-05).
            MissingDoctorCredentialsError: If doctor has no registered CMP or RNE.
            InvalidMachineOperationError: If the workstation is not authorized
                to handle legal documents (RN-16).
            DomainError: If the report is not found.
            ImmutableReportError: If the report is already signed (RN-06).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            SignReportResponse: Dictionary with ``report_id`` and ``signed_at`` timestamp.
        """
        log.info(
            "SignReport: started. report_id='%s', ip='%s'.",
            request.report_id,
            request.requester_ip,
        )

        # RN-05 / RN-16: Validate doctor role and credentials via common service.
        current_user = await self._current_user_service.get_current_user()
        authorize(IsDoctor(), context=StandardContext(subject=current_user))

        # RN-16: Validate workstation authorization for legal document operations.
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
                operation="sign_report",
            )

        # Hydrate report with exclusive lock for the signing transaction.
        report_entity_id = EntityID(value=request.report_id)
        report = await self._report_gateway.read_by_id(
            report_entity_id, for_update=True
        )
        if report is None:
            raise DomainError(f"Report '{request.report_id}' not found.")

        # RN-06: ``Report.sign`` raises ``FinalizeReport`` if already signed.
        from src.dev.domain.value_objects.report import ReportSignature

        # Build a deterministic signature hash from doctor credentials + content.
        legal_sig = current_user.legal_signature
        raw_hash = (
            f"{legal_sig}:{report.exam_code.value}:{report.content.value}"
        ).encode("utf-8")
        import hashlib

        digest = hashlib.sha256(raw_hash).digest()

        try:
            report.sign(ReportSignature(hash=digest))
        except Exception as exc:
            raise ImmutableReportError(report_id=request.report_id) from exc

        await self._flusher.flush()
        await self._transaction_manager.commit()

        signed_at = datetime.now(tz=timezone.utc).isoformat()
        log.info(
            "SignReport: done. report_id='%s', signed_at='%s'.",
            request.report_id,
            signed_at,
        )
        return SignReportResponse(report_id=request.report_id, signed_at=signed_at)
