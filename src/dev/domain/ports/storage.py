"""Ports for image storage."""

from typing import Protocol

from src.dev.domain.entities.image import Image
from src.dev.domain.value_objects.exam import ExamID


class ImageStoragePort(Protocol):
    """Protocols for image storage"""

    async def store(self, exam_id: ExamID, files: list[Image]) -> None:
        """Store images for a given exam ID."""

    async def exists_for_exam(self, exam_id: ExamID) -> bool:
        """Check if images exist for a given exam ID."""
        ...
