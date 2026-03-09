"""Domain service for exam creation"""

from src.dev.domain.entities.exam import Exam
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import (
    PatientRepository,
    WorkstationRepository,
)
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.patient import PatientHC
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import NetworkAddress


class ExamCreatorService:
    """Service to handle the creation of exams enforcing domain rules."""

    def __init__(
        self,
        patient_repository: PatientRepository,
        workstation_repository: WorkstationRepository,
    ) -> None:
        self._patient_repository = patient_repository
        self._workstation_repository = workstation_repository

    async def create_exam(
        self,
        id_: EntityID,
        exam_code: ExamCode,
        patient_hc: PatientHC,
        modality: Modality,
        study_type: str,
        workstation_network: NetworkAddress,
    ) -> Exam:
        """
        Creates a new Exam.

        Enforces rules:
        - RN-01, RN-02: Patient must exist and have a valid HC.
        - RN-09: Workstation must be of type ACQUISITION to create exams.
        """
        # Validate Patient (RN-01, RN-02)
        patient_exists = await self._patient_repository.exists_by_hc(patient_hc)
        if not patient_exists:
            raise DomainError(f"Patient with HC {patient_hc.value} does not exist.")

        # Validate Workstation (RN-09)
        workstation = await self._workstation_repository.get_by_network(
            workstation_network
        )
        if workstation is None:
            raise DomainError("Workstation not found for the given network address.")

        if not workstation.can_upload_file:
            raise DomainError(
                "Only authorized ACQUISITION workstations can create exams."
            )

        # Create the Exam entity
        return Exam(
            id_=id_,
            exam_code=exam_code,
            patient_HC=patient_hc,
            modality=modality,
            study_type=study_type,
            status=ExamStatus.PENDING,
        )
