"""Upload Exam Image — Command Interactor

Use case: Attach a DICOM image file to an existing exam. Only permitted from
authorized ACQUISITION workstations (RN-04, RN-09, RN-10).
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
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.workstation_gateway import WorkstationQueryGateway
from src.dev.domain.entities.image import Image
from src.dev.domain.enum.images import ImageType
from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.imageFiles import ImageReference
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadImageRequest:
    """Input DTO for UploadExamImageInteractor.

    Attributes:
        exam_id: Unique identifier of the exam to which the image will be linked.
        image_url: Secure HTTPS URL of the DICOM file already uploaded to the
            storage backend (e.g. S3 pre-signed URL or CDN path).
        file_size_bytes: Byte size of the uploaded file for bookkeeping.
        requester_ip: IPv4 address of the requesting station — used to enforce
            ACQUISITION-only access (RN-09, RN-10).
    """

    exam_id: UUID
    image_url: str
    file_size_bytes: int
    requester_ip: str


class UploadImageResponse(TypedDict):
    """Output DTO for UploadExamImageInteractor."""

    image_id: UUID
    exam_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class UploadExamImageInteractor:
    """Associates a DICOM image with an existing exam.

    Enforced rules:
    - RN-09 / RN-10: Only authorized ACQUISITION workstations may upload images.
    - RN-04: An exam in REPORTED status cannot receive new images.

    The domain entity ``Exam.add_image`` enforces both the status guard and
    tracks the INCOMPLETE state transition automatically.

    Dependencies:
        exam_command_gateway: Hydrates and persists the Exam aggregate.
        workstation_query_gateway: Validates the requesting terminal by IP.
        flusher: Flushes the ORM buffer so constraint violations surface early.
        transaction_manager: Commits the active unit of work.
    """

    def __init__(
        self,
        exam_command_gateway: ExamCommandGateway,
        workstation_query_gateway: WorkstationQueryGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._exam_gateway = exam_command_gateway
        self._workstation_gateway = workstation_query_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: UploadImageRequest) -> UploadImageResponse:
        """Attach a DICOM image to an exam from an authorized ACQUISITION station.

        Args:
            request: Validated input DTO with exam ID, image URL, and requester IP.

        Raises:
            InvalidMachineOperationError: If the calling station is not an authorized
                ACQUISITION workstation (RN-09, RN-10).
            DomainError: If no exam with the given ``exam_id`` exists.
            ValueError: If the exam is already in REPORTED status (RN-04),
                or if a DICOM image invariant (metadata presence) is violated.
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            UploadImageResponse: Dictionary with the new ``image_id`` and ``exam_id``.
        """
        log.info(
            "UploadExamImage: started. exam_id='%s', ip='%s'.",
            request.exam_id,
            request.requester_ip,
        )

        # RN-09/RN-10: Machine classification check.
        workstation = await self._workstation_gateway.read_by_ip(request.requester_ip)
        if (
            workstation is None
            or not workstation["is_authorized"]
            or workstation["type"] != WorkstationType.ACQUISITION
        ):
            machine_type = str(workstation["type"]) if workstation else "UNKNOWN"
            machine_id = (
                str(workstation["id_"]) if workstation else request.requester_ip
            )
            raise InvalidMachineOperationError(
                machine_id=machine_id,
                machine_type=machine_type,
                operation="upload_exam_image",
            )

        # Hydrate exam aggregate with an exclusive lock.
        exam_entity_id = EntityID(value=request.exam_id)
        exam = await self._exam_gateway.read_by_id(exam_entity_id, for_update=True)
        if exam is None:
            raise DomainError(f"Exam '{request.exam_id}' not found.")

        # Build the Image entity.  STATIC type is used when no DICOM metadata is
        # provided at this stage — the modality layer can enrich it later.
        image_id = EntityID(value=uuid4())
        image = Image(
            id_=image_id,
            exam_id=exam_entity_id,
            image_type=ImageType.STATIC,
            reference=ImageReference(
                url=request.image_url,
                file_size_bytes=request.file_size_bytes,
                mime_type="application/dicom",
            ),
        )

        # Domain entity enforces RN-04: raises ValueError if exam is REPORTED.
        exam.add_image(image)

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "UploadExamImage: done. image_id='%s', exam_id='%s'.",
            image_id.value,
            request.exam_id,
        )
        return UploadImageResponse(image_id=image_id.value, exam_id=request.exam_id)
