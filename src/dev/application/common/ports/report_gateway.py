"""Report Gateways — Application Layer Ports

Contracts segregating write and read access to the Report aggregate,
supporting immutability of signed reports and amendment versioning (RN-05, RN-06, RN-07).
"""

from abc import abstractmethod
from datetime import datetime
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.entities.report import Report
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.user import EntityID

# ---------------------------------------------------------------------------
# Query Models (TypedDicts — plain data, no domain behaviour)
# ---------------------------------------------------------------------------


class ReportQM(TypedDict):
    """Flat read model for a single report version."""

    id_: UUID
    report_num: str
    exam_code: str
    doctor_id: UUID
    content: str
    is_final: bool
    version: int
    signed_at: datetime | None


class ReportHistoryQM(TypedDict):
    """
    Full version history of a report associated to an exam.
    Used by the report history query service (RN-06).
    """

    exam_code: str
    versions: list[ReportQM]
    total_versions: int


# ---------------------------------------------------------------------------
# Command Gateway — mutable access, works with rich domain entities
# ---------------------------------------------------------------------------


class ReportCommandGateway(Protocol):
    """
    Contract to write operations on the report aggregate.

    Manages the lifecycle of drafts, signing,
    and prevents mutation of already signed reports (RN-06, RN-07).
    """

    @abstractmethod
    def add(self, report: Report) -> None:
        """
        :raises DataMapperError:

        Persist a new report (initial draft or amendment version).
        The ID and version are assigned in the domain before this method is called.
        """

    @abstractmethod
    async def read_by_id(
        self,
        report_id: EntityID,
        for_update: bool = False,
    ) -> Report | None:
        """
        :raises DataMapperError:

        Recover a report by its internal ID, optionally with an exclusive lock
        for writing within the active transaction.
        """

    @abstractmethod
    async def read_by_exam_code(
        self,
        exam_code: ExamCode,
        for_update: bool = False,
    ) -> Report | None:
        """
        :raises DataMapperError:

        Recover the active report (latest version) linked to an exam.
        Used to signed or amend an existing report (RN-06, RN-07).
        """


# ---------------------------------------------------------------------------
# Query Gateway — read-only projections, never returns domain entities
# ---------------------------------------------------------------------------


class ReportQueryGateway(Protocol):
    """
    Contract for projected readings on reports.

    Returns DTOs plains without moisturizing the aggregate Report.
    """

    @abstractmethod
    async def read_history(self, exam_code: ExamCode) -> ReportHistoryQM:
        """
        :raises ReaderError:

        Return the complete version history (original + amendments)
        of a report associated to an exam(RN-06).
        de un informe asociado a un examen (RN-06).
        """
