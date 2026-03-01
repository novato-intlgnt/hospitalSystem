"""Report entity"""

from uuid import UUID

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.exam import ExamID
from src.dev.domain.value_objects.user import EntityID


class Report(BaseEntity[EntityID]):
    """Report entity"""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_id: ExamID,
        doctor_id: UUID,
        content: str,
        signature_hash: str,
        is_final: bool = False,
    ) -> None:
        super().__init__(id_=id_)
        self._exam_id = exam_id
        self._doctor_id = doctor_id
        self._content = content
        self._signature_hash = signature_hash
        self._is_final = is_final
        self._version = 1

    def update_content(self, content: str) -> None:
        """Update report content"""
        if self._is_final:
            raise ValueError("Cannot update content of a final report")
        self._content = content
        self._version += 1
