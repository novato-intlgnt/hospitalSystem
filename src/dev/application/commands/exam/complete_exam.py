"""Complete Exam — Command Interactor

Use case: Advance an exam to REPORTED status after verifying that at least
one DICOM image has been associated with it (RN-03, RN-04).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from src.dev.application.common.exceptions.invalid_state_transition import (
    InvalidExamStateTransitionError,
)
from src.dev.application.common.ports.exam_gateway import ExamCommandGateway
from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CompleteExamRequest:
    """Input DTO for CompleteExamInteractor.

    Attributes:
        exam_id: Unique identifier of the exam to mark as REPORTED.
    """

    exam_id: UUID


class CompleteExamResponse(TypedDict):
    """Output DTO for CompleteExamInteractor."""

    exam_id: UUID
    status: str


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class CompleteExamInteractor:
    """Marks an exam as REPORTED after validating image completeness.

    Enforced rules:
    - RN-03: State transition is only valid when the exam holds at least one image.
    - RN-04: The domain entity ``Exam.mark_as_reported`` enforces both the state
      guard and the image-presence invariant — any violation surfaces as a
      ``DomainError`` which is re-mapped to ``InvalidExamStateTransitionError``.

    No authentication context is required here — workstation-level controls
    validate the upstream request; this use case focuses solely on the state machine.

    Dependencies:
        exam_command_gateway: Hydrates and persists the Exam aggregate.
        flusher: Flushes pending ORM state before commit.
        transaction_manager: Commits the active unit of work.
    """

    def __init__(
        self,
        exam_command_gateway: ExamCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._exam_gateway = exam_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: CompleteExamRequest) -> CompleteExamResponse:
        """Transition the exam to REPORTED status.

        Args:
            request: Input DTO containing the target ``exam_id``.

        Raises:
            DomainError: If the exam is not found.
            InvalidExamStateTransitionError: If the exam lacks images or is already
                in REPORTED status (RN-03, RN-04).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            CompleteExamResponse: Dictionary with the ``exam_id`` and final ``status``.
        """
        log.info("CompleteExam: started. exam_id='%s'.", request.exam_id)

        exam_entity_id = EntityID(value=request.exam_id)
        exam = await self._exam_gateway.read_by_id(exam_entity_id, for_update=True)
        if exam is None:
            raise DomainError(f"Exam '{request.exam_id}' not found.")

        # Delegate state machine and image-presence guard to the domain entity.
        try:
            exam.mark_as_reported()
        except DomainError as exc:
            raise InvalidExamStateTransitionError(
                exam_id=request.exam_id,
                from_state=str(exam.status),
                to_state="REPORTED",
            ) from exc

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "CompleteExam: done. exam_id='%s', status='%s'.",
            request.exam_id,
            exam.status,
        )
        return CompleteExamResponse(exam_id=request.exam_id, status=str(exam.status))
