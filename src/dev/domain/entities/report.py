"""Report entity"""

from uuid import UUID

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.exceptions.report import FinalizeReport
from src.dev.domain.value_objects.doctor import DoctorID
from src.dev.domain.value_objects.exam import ExamID, ReportContent, ReportSignature
from src.dev.domain.value_objects.user import EntityID


class Report(BaseEntity[EntityID]):
    """Report aggregate root"""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_id: ExamID,
        doctor_id: EntityID,
        content: ReportContent,
        signature: ReportSignature | None = None,
        version: int = 1,
    ) -> None:
        super().__init__(id_=id_)
        self._exam_id = exam_id
        self._doctor_id = doctor_id
        self._content = content
        self._signature = signature
        self._version = version

    @property
    def is_final(self) -> bool:
        return self._signature is not None

    @property
    def version(self) -> int:
        return self._version

    def update_content(self, content: ReportContent) -> None:
        if self.is_final:
            raise FinalizeReport(self.id_)

        self._content = content
        self._version += 1
