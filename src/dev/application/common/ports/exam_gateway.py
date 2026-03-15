"""Exam Gateways — Application Layer Ports

Contracts segregating write and read access to the Exam aggregate,
covering the full diagnostic imaging workflow (RN-02, RN-03, RN-04, RN-11).
"""

from abc import abstractmethod
from datetime import date
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.entities.exam import Exam
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.user import EntityID

# ---------------------------------------------------------------------------
# Query Models (TypedDicts — plain data, no domain behaviour)
# ---------------------------------------------------------------------------


class ImageQM(TypedDict):
    """Flat read model for a DICOM image attached to an exam."""

    id_: UUID
    file_path: str
    modality: Modality
    uploaded_at: date


class ExamDetailsQM(TypedDict):
    """
    Full exam detail read model — includes nested images.
    Used by visualization workstations (RN-11).
    """

    id_: UUID
    exam_code: str
    patient_hc: str
    modality: Modality
    study_type: str
    status: ExamStatus
    exam_date: date
    images: list[ImageQM]


class ExamSummaryQM(TypedDict):
    """Lightweight exam read model for grid/list views."""

    id_: UUID
    exam_code: str
    patient_hc: str
    modality: Modality
    study_type: str
    status: ExamStatus
    exam_date: date


class ListExamsQM(TypedDict):
    """Paginated result of exam summaries."""

    exams: list[ExamSummaryQM]
    total: int


# ---------------------------------------------------------------------------
# Command Gateway — mutable access, works with rich domain entities
# ---------------------------------------------------------------------------


class ExamCommandGateway(Protocol):
    """
    Contract to write operations on the Exam aggregate.

    Manages the exam lifecycle from creation to report viewed (RN-02, RN-03, RN-04).
    """

    @abstractmethod
    def add(self, exam: Exam) -> None:
        """
        :raises DataMapperError:

        Persist a new exam just created in PENDING status.
        Persiste un nuevo examen recién creado en estado PENDING.
        """

    @abstractmethod
    async def read_by_id(
        self,
        exam_id: EntityID,
        for_update: bool = False,
    ) -> Exam | None:
        """
        :raises DataMapperError:

        Recovers an exam by its internal ID,
        optionally locking it for update within the active transaction.
        """

    @abstractmethod
    async def read_by_code(
        self,
        exam_code: ExamCode,
        for_update: bool = False,
    ) -> Exam | None:
        """
        :raises DataMapperError:

        Recovers an exam by its unique clinical code (RN-02).
        To verify duplicates or hydrate the aggregate in commands.
        """


# ---------------------------------------------------------------------------
# Query Gateway — read-only projections, never returns domain entities
# ---------------------------------------------------------------------------


class ExamQueryGateway(Protocol):
    """
    Contract for reads dense and optimized for exams.

    Implementations execute direct SQL projecting DTOs.
    Never returns rich domain entities.
    """

    @abstractmethod
    async def read_details(self, exam_code: ExamCode) -> ExamDetailsQM | None:
        """
        :raises ReaderError:

        Return the full details of an exam, including image URLs,
        for visualization stations (RN-11).
        """

    @abstractmethod
    async def read_all(
        self,
        limit: int,
        offset: int,
        status: ExamStatus | None = None,
        patient_hc: str | None = None,
    ) -> ListExamsQM:
        """
        :raises ReaderError:

        Returns a paginated list of exams filterable by status and
        patient's clinical history for the worklist grid.
        """
