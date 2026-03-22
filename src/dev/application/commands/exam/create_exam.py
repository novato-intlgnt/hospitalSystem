"""Create Exam — Command Interactor

Use case: Create a new exam in PENDING status for an existing patient, restricted
to ACQUISITION workstations requesting via their registered IP (RN-02, RN-09).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

from src.dev.application.common.exceptions.invalid_machine_op import (
    InvalidMachineOperationError,
)
from src.dev.application.common.ports.exam_gateway import ExamCommandGateway
from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.patient_gateway import PatientCommandGateway
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.workstation_gateway import WorkstationQueryGateway
from src.dev.domain.entities.exam import Exam
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.patient import PatientHC
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateExamRequest:
    """Input DTO for CreateExamInteractor.

    Attributes:
        patient_hc: Clinical History code linking the exam to an existing patient.
        exam_code: Unique clinical code assigned to this imaging study (RN-02).
        modality: Imaging modality (e.g. CT, MRI, X-Ray).
        study_type: Free-text description of the study protocol requested.
        requester_ip: IPv4 address of the requesting station — used to enforce
            that only ACQUISITION workstations can create exams (RN-09).
    """

    patient_hc: str
    exam_code: str
    modality: Modality
    study_type: str
    requester_ip: str


class CreateExamResponse(TypedDict):
    """Output DTO for CreateExamInteractor."""

    exam_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class CreateExamInteractor:
    """Creates a diagnostic exam and links it to an existing patient.

    Enforced rules:
    - RN-09: The request must originate from a registered ACQUISITION workstation
      (validated via the ``requester_ip``).
    - RN-02: The exam code must be unique; the gateway enforces this at flush.
    - RN-03: The exam is created in PENDING status.

    Dependencies:
        exam_command_gateway: Write access to the Exam aggregate.
        patient_command_gateway: Validates that the patient exists by HC.
        workstation_query_gateway: Classifies the calling terminal by IP.
        flusher: Surfaces DB constraint violations before commit.
        transaction_manager: Commits the active unit of work.
    """

    def __init__(
        self,
        exam_command_gateway: ExamCommandGateway,
        patient_command_gateway: PatientCommandGateway,
        workstation_query_gateway: WorkstationQueryGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._exam_gateway = exam_command_gateway
        self._patient_gateway = patient_command_gateway
        self._workstation_gateway = workstation_query_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: CreateExamRequest) -> CreateExamResponse:
        """Create a new exam linked to a patient from an authorized workstation.

        Args:
            request: Validated input DTO with exam details and requester IP.

        Raises:
            InvalidMachineOperationError: If the requesting IP is not a registered
                ACQUISITION workstation (RN-09).
            DomainError: If the patient HC does not exist in the system.
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            CreateExamResponse: Dictionary containing the new ``exam_id``.
        """
        log.info(
            "CreateExam: started. exam_code='%s', patient_hc='%s', ip='%s'.",
            request.exam_code,
            request.patient_hc,
            request.requester_ip,
        )

        # RN-09: Verify requesting workstation is ACQUISITION type.
        workstation = await self._workstation_gateway.read_by_ip(request.requester_ip)
        if workstation is None or not workstation["is_authorized"]:
            raise InvalidMachineOperationError(
                machine_id=request.requester_ip,
                machine_type="UNKNOWN",
                operation="create_exam",
            )
        from src.dev.domain.enum.workstation import WorkstationType

        if workstation["type"] != WorkstationType.ACQUISITION:
            raise InvalidMachineOperationError(
                machine_id=str(workstation["id_"]),
                machine_type=str(workstation["type"]),
                operation="create_exam",
            )

        # Verify patient exists (RN-01, RN-02).
        patient_hc = PatientHC(value=request.patient_hc)
        patient = await self._patient_gateway.read_by_hc(patient_hc)
        if patient is None:
            raise DomainError(f"Patient with HC '{request.patient_hc}' does not exist.")

        exam_id = EntityID(value=uuid4())
        exam = Exam(
            id_=exam_id,
            exam_code=ExamCode(value=request.exam_code),
            patient_HC=patient_hc,
            modality=request.modality,
            study_type=request.study_type,
            status=ExamStatus.PENDING,
        )

        self._exam_gateway.add(exam)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info("CreateExam: done. exam_id='%s'.", exam_id.value)
        return CreateExamResponse(exam_id=exam_id.value)
